# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
> #3170（2026-11-23 17:23, 放行autoqueue令·监控巡检·daemon idle无eval负载·**backlog 270k-296k全清15ckpt(directive#1✅维持)**·训练健康iter=297280/700000(42.47%) step_avg(last15)=7115ms(7.12s,median7106,min6997,max7249,0/15>7.4s✅)·loss≈1.99(1.987-2.005) 0NaN/0skip✅ lr=1e-3·load(directive#2) .29=24.63/23.70/23.54✅/.12=24.06/25.05/25.11✅(no llama-server,eval idle)·**step-time(directive#3):无eval负载(daemon idle+no llama-server),baseline avg=7115ms(7.12s)<7.4s gate✅,0/15>7.4s=训练jitter干净无spike**·daemon alive(PID1081392 etimes≈163594s≈45.4h,idle cycling300s,last idle@17:23:10)·298k NOT on disk(training at 297280,save-interval=2000,next ckpt 298000,~720iter@7.12s≈86min,ETA~18:49)·**L1 harness-avg(directive二.1全写出):270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.63/284k58.25/286k59.88/288k58.50/290k55.25/292k60.63/294k59.00/296k59.12**·L1报告40/40ckpt@16:27含296k=59.12%✅(35236B)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter297280@17:23:16) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@17:23:10) ckpt=.../nemo_experiments/baize2b/checkpoints/iter_0296000(298k absent) eval_json=.../nemo_experiments/baize2b/lm_eval_results/gguf_iter_296000_fixed_8set/results.json(26002B@16:17,8tasks:arc_c/arc_e/boolq/hellaswag/obqa/piqa/sciq/wino✅) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(35236B@16:27,40/40ckpt含296k)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈30.5KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-23.md
> #3169（2026-11-23 17:09, 放行autoqueue令·监控巡检·daemon idle无eval负载·**backlog 270k-296k全清15ckpt(directive#1✅维持)**·训练健康iter=297160/700000(42.45%) step_avg(last15)=7186ms(7.19s,median7090,min6997,max8152,2/15>7.4s=transient非持续)·loss≈2.00(1.983-2.005) 0NaN/0skip✅ lr=1e-3·load(directive#2) .29=22.53/23.41/23.65✅/.12=23.84/24.59/24.87✅(no llama-server,eval idle;pgrep .12无MegaMath CPU争抢✅)·**step-time(directive#3):无eval负载(daemon idle+no llama-server),baseline avg=7186ms(7.19s)<7.4s gate✅,2/15瞬时spike(8152ms@297100,7299ms@297090)非持续=训练jitter非eval所致**·daemon alive(PID1081392 etimes≈162730s≈45.2h,idle cycling300s,last idle@17:08:09)·298k NOT on disk(training at 297160,save-interval=2000,next ckpt 298000,~840iter@7.19s≈101min,ETA~18:50)·**L1 harness-avg(directive二.1全写出):270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.63/284k58.25/286k59.88/288k58.50/290k55.25/292k60.63/294k59.00/296k59.12**·L1报告40/40ckpt@16:27含296k=59.12%✅(35236B)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter297160@17:09:02) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@17:08:09) ckpt=.../nemo_experiments/baize2b/checkpoints/iter_0296000(298k absent) eval_json=.../nemo_experiments/baize2b/lm_eval_results/gguf_iter_296000_fixed_8set/results.json(26002B@16:17,8tasks:arc_c/arc_e/boolq/hellaswag/obqa/piqa/sciq/wino✅) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(35236B@16:27,40/40ckpt含296k)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈30.5KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-23.md
> 📦 #3168（2026-11-23 17:03, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=297110 step7.11s(0/15>7.4s✅)·load .29=22.14/.12=23.79✅·backlog全清·298k NOT on disk(ETA~18:49)）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3167（2026-11-23 16:51, 放行autoqueue令·监控巡检·daemon idle无eval负载·**backlog 270k-296k全清15ckpt(directive#1✅维持)**·训练健康iter=297000/700000(42.43%) step_avg(last15)=7271ms(7.27s,median7180,min7015,max8553,2/15>7.4s=transient无eval抖动非持续)·loss≈2.00(1.994-2.003) 0NaN/0skip✅ lr=1e-3·load(directive#2) .29=23.96/25.22/24.56✅/.12=26.90/26.56/25.87✅(no llama-server,eval idle)·**step-time(directive#3):无eval负载(daemon idle+no llama-server),baseline avg=7271ms(7.27s)<7.4s gate✅,2/15瞬时spike(8553ms)非持续=训练jitter非eval所致**·daemon alive(PID1081392 etimes≈161578s≈44.9h,idle cycling300s等298k)·298k NOT on disk(training at 297000,save-interval=2000,next ckpt 298000,ETA~18:51)·L1报告40/40ckpt@16:27含296k=59.12%✅(35236B)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter297000@16:49:54) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@16:48:06) ckpt=.../checkpoints/iter_0296000 eval_json=.../lm_eval_results/gguf_iter_296000_fixed_8set/results.json(26002B@16:17,8tasks:arc_c/arc_e/boolq/hellaswag/obqa/piqa/sciq/wino✅) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(35236B@16:27,40/40ckpt含296k)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈27.3KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-23.md

> #3166（2026-11-23 16:41, 放行autoqueue令·监控巡检·daemon idle无eval负载·**backlog 270k-296k全清15ckpt(directive#1✅维持)**·训练健康iter=296950/700000(42.42%) step_avg(last15)=7261ms(7.26s,median7109,min6992,max8553,2/15>7.4s=transient无eval抖动非持续)·loss≈1.99(1.985-2.013) 0NaN/0skip✅ lr=1e-3·load(directive#2) .29=22.26/23.37/23.95✅/.12=27.68/26.04/25.29✅(no llama-server,eval idle)·**step-time(directive#3):无eval负载(daemon idle+no llama-server),baseline avg=7261ms(7.26s)<7.4s gate✅,2/15瞬时spike(8553ms@296880,7967ms@296930)非持续=训练jitter非eval所致**·daemon alive(PID1081392 etimes≈161032s≈44.8h,idle cycling300s等298k)·298k NOT on disk(training at 296950,save-interval=2000,next ckpt 298000,ETA~18:50)·L1报告40/40ckpt@16:27含296k=59.12%✅(35236B)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter296950@16:40:16) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@16:38:05) ckpt=.../checkpoints/iter_0296000 eval_json=.../lm_eval_results/gguf_iter_296000_fixed_8set/results.json(26002B@16:17,8tasks:arc_c/arc_e/boolq/hellaswag/obqa/piqa/sciq/wino✅) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(35236B@16:27,40/40ckpt含296k)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈25.8KB<32KB✅）→ daily-memories/2026-11-23.md

> 📦 #3165（2026-11-23 16:33, 放行autoqueue令·监控巡检·daemon idle无eval负载·**backlog 270k-296k全清15ckpt(directive#1✅)**·训练健康iter=296840/700000(42.41%) step_avg(last15)=7166ms(7.17s,6995-8366,median7083)·loss≈1.98(1.980-2.013) 0NaN/0skip✅ lr=1e-3·load(directive#2) .29=26.50/24.92/24.70✅/.12=24.46/25.60/24.81✅(no llama-server,eval idle)·**step-time(directive#3):无eval负载(daemon idle+no llama-server),baseline=7166ms(7.17s)<7.4s gate✅**·daemon alive(PID1081392 etimes≈160484s≈44.6h,idle cycling300s等298k)·298k NOT on disk(training at 296840,save-interval=2000,next ckpt 298000,ETA~18:46)·L1报告40/40ckpt@16:27含296k=59.12%✅(35236B)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter296840@16:30:31) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@16:28:04) ckpt=.../checkpoints/iter_0296000 eval_json=.../lm_eval_results/gguf_iter_296000_fixed_8set/results.json(26002B@16:17✅) report=.../reports/report_pretrain_llamacpp_scaling_zh.html(40/40ckpt@16:27,35236B)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈24.6KB<32KB✅ TASK≈24.7KB<32KB✅）→ daily-memories/2026-11-23.md

> 📦 #3164（2026-11-23 16:18, 放行autoqueue令·**296k eval DONE✅ harness-avg=59.12%(>294k59.00%)**·训练健康iter=296680/700000(42.38%) step=7099ms(last)·loss≈2.00 0NaN/0skip✅·**step-time(directive#3):pre-eval=7.10s→during-eval(avg80iter=7165ms,10/80>7.4s gate,spike16:06-16:13 max8456ms⚠️transient)→post-eval=7060ms✅**·**⚠️step-time spike观察:eval第62-69min(16:06-16:13)出现7min持续>7.4s(5/7iter),likely lm_eval CPU-intensive task;自愈(eval仍在跑时回落);训练0NaN/0skip健康;daemon将在298k前health-gate自动pause if>7.4s;未escalate待运维**·load(directive#2) post-eval .29=24.68/25.09/25.68✅/.12=23.64/23.63/23.78✅·daemon alive(PID1081392 etimes≈159700s≈44.3h,idle等298k)·**backlog 270k-296k全清15ckpt(directive#1✅全完成)**·**L1 harness-avg:270k59.75/272k56.75/274k60.00/276k58.13/278k57.38/280k58.38/282k58.63/284k58.25/286k59.88/288k58.50/290k55.25/292k60.63/294k59.00/296k59.12**·L1报告35236B@16:17含296k=59.12%✅(40/40ckpt,daemon Phase6自动刷新DONE)·296k individual:arc_c36/arc_e61/boolq66/hellaswag54/obqa36/piqa76/sciq85/wino59·next ckpts:298k ETA~18:46/300k ETA~22:40·298k NOT on disk(training at 296680,save-interval=2000,next ckpt 298000)·evidence:ckpt=.../checkpoints/iter_0296000 eval_json=.../lm_eval_results/gguf_iter_296000_fixed_8set/results.json(26002B@16:17✅) worker=/tmp/baize_s1_baize2b_worker.log(iter296680@16:18) daemon=/tmp/baize_l1_autoqueue_continuous.log(iter296000 DONE@16:17:33) report=.../reports/report_pretrain_llamacpp_scaling_zh.html(35236B@16:17✅)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈24.2KB<32KB✅ TASK≈24.7KB<32KB✅）→ daily-memories/2026-11-23.md

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

> #3142（2026-11-23 12:10, 放行autoqueue令·监控巡检·**294k eval DONE✅Avg=59.00%**(10:48:49起→12:02:55完,74min,daemon idle等296k)·训练健康iter=294690/700000(42.10%) step_avg(last10,post-eval)=7222ms(7.22s,7216-7228,median7222)·loss≈2.00 0NaN/0skip✅ lr=1e-3·load .29=26.61/28.07/28.27✅(nproc224,no llama-server,eval done)/.12=24.19/25.53/25.76✅(no llama-server)·**step-time测量(directive#3):eval完成·pre-eval baseline(#3138)=7345ms(7.35s)→during-eval avg=7280ms(7.28s,impact=-66ms)→post-eval=7222ms(7.22s),eval未拖训练✅,全程<7.4s gate**·daemon idle(PID1081392 alive etimes≈145000s≈40.3h,sleep300s等296k,296k NOT on disk)·L1报告39/40ckpt@12:09含294k=59.00%✅(34753B,daemon已自动刷新)·backlog 270k-294k全清14ckpt·**294k=59.00%**(arc_c32/arc_e68/boolq59/hella55/obqa35/piqa77/sciq85/wino61)·296k NOT on disk(training at 294690,next ckpt 296000)·research日报2026-11-23:pretrain建议2条(任务族分层规模收益检查/GPT-NeoX few-shot口径复核)→纳入待评估,本轮纯监控未执行·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter294690@12:10) daemon=/tmp/baize_l1_autoqueue_continuous.log(iter=294000 DONE@12:02:55) results=.../code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_294000_fixed_8set/results.json(25988B@12:02) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(39/40ckpt@12:09,34753B)·GGUF已清理·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈27KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-23.md
> 📦 §#3138–#3141（2026-11-23 11:16–11:52, 放行autoqueue令·294k eval RUNNING监控4轮·eval未拖训练step~7.35-7.57s(NOT persistent>7.4s)·294k于12:02 DONE Avg=59.00% 见#3142）→ daily-memories/2026-11-23.md；需要时再读。


> #3137（2026-11-23 10:37, 放行autoqueue令·监控巡检·daemon idle无eval负载·**backlog 270k-292k全清13ckpt(directive#1每ckpt L1分数见WAITING行,均8/8集有效✅)**·训练健康iter=293940/700000(41.99%) step_avg(last15)=7392ms(7.39s,7213-7833,median7381)·loss≈1.998(1.985-2.008) 0NaN/0skip✅ lr=1e-3·load .29=26.77/25.07/25.36✅/.12=26.18/26.45/26.41✅(no llama-server,load正常)·**step-time测量(directive#3):无eval负载(daemon idle+pgrep -x llama-server=0),baseline=7392ms(7.39s)<7.4s gate✅,非eval致**·daemon idle(PID1081392 alive etimes≈139224s≈38.7h,sleep300s等294k,294k NOT on disk,ETA≈10:45,iter=293940需60步,盘上最新=iter_0292000)·L1报告38/39ckpt@08:09含292k=60.63%✅(34285B,results落盘.../lm_eval_results/gguf_iter_292000_fixed_8set/results.json 26002B@08:02)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter293940@10:37:40) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@10:37:55) report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(38/39ckpt@08:09)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈25KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-23.md


> 📦 #3135–#3136（2026-11-23 10:19–10:29, 放行autoqueue令·daemon idle监控巡检2轮·backlog全清270k-292k·训练健康step~7.39-7.41s(微触7.4s gate,daemon idle确认非eval致)·load正常·294k NOT on disk ETA≈10:44）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3130–#3134（2026-11-23 09:32–10:10, 放行autoqueue令·daemon idle监控巡检5轮·backlog全清270k-292k 13ckpt·训练健康step~7.37-7.42s(微触7.4s gate,daemon idle确认非eval致)·load正常·294k NOT on disk ETA≈10:45）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3129（2026-11-23 09:23, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清·训练健康iter=293330 step7374ms<gate·daemon idle等294k ETA≈10:43）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3128（2026-11-23 09:10, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-292k全清13ckpt·训练健康iter=293230 step_avg≈7409ms(7.41s微越gate,非eval致)·load .29=29.91/.12=26.25✅·daemon idle等294k ETA≈10:45）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3127（2026-11-23 09:05, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-292k全清13ckpt·训练健康iter=293190 step_avg≈7390ms(<gate✅,近40min从7.2s缓升至7.4s,非eval致)·load .29=25.17/.12=25.54✅·daemon idle等294k ETA≈10:44）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3126（2026-11-23 08:53, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-292k全清13ckpt·训练健康iter=293090 step_avg≈7341ms(<gate✅)·load .29=25.42/.12=26.10✅·daemon idle等294k ETA≈10:43）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3125（2026-11-23 08:48, 放行autoqueue令·监控巡检·daemon idle·backlog全清·训练健康iter=293040 step7286ms<gate → daily-memories/2026-11-23.md；需要时再读。
> 📦 #3124（2026-11-23 08:40, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-292k全清13ckpt·训练健康iter=292980 step_avg(last15)=7286ms(7079-7488)·last3步略>7.4s但daemon idle→正常波动NOT eval-caused·loss≈1.98 0NaN/0skip → daily-memories/2026-11-23.md；需要时再读。
> 📦 #3123（2026-11-23 08:31, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清·训练健康iter=292900 step7212ms<gate → daily-memories/2026-11-23.md；需要时再读。
> 📦 #3122（2026-11-23 08:25, 放行autoqueue令·监控巡检·daemon idle·backlog全清·训练健康iter=292850 step7208ms<gate → daily-memories/2026-11-23.md；需要时再读。
> 📦 #3121（2026-11-23 08:18, 放行autoqueue令·监控巡检·daemon idle·backlog 270k-292k全清13ckpt·训练健康iter=292800 step7249ms<gate loss≈1.99 → daily-memories/2026-11-23.md；需要时再读。
> 📦 #3120（2026-11-23 08:05, 放行autoqueue令·**292k eval DONE✅Avg=60.63%**(38th ckpt,过迆最高)·per-task:arc_c39/arc_e66/boolq65/hella46/obqa25/piqa79/sciq87/wino66·step-time三段:pre7.28s→during avg7199ms(全<7.4s gate✅)→post7174ms·eval未拖训练·backlog 270k-292k全清13ckpt(270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62/284k58.25/286k59.88/288k58.50/290k55.25/292k60.63)·results=.../lm_eval_results/gguf_iter_292000_fixed_8set/results.json → daily-memories/2026-11-23.md；需要时再读。

> 📦 #3115–#3119（2026-11-23 07:25–07:56, 292k eval RUNNING监控5轮interim,step均<7.4s gate✅,eval未拖训练 → 08:02完DONE Avg=60.63% 见#3120）→ daily-memories/2026-11-23.md
> 📦 §#3108–#3111（2026-11-23 06:28–06:53, 放行autoqueue令·292k eval RUNNING监控轮4条·backlog全清270k-290k 11ckpt·训练健康step~7.05-7.34s·load正常·daemon eval 292k 06:45起）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3107（2026-11-23 06:22, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291840/700000(41.69%) step_avg(last10)=7256ms(<7.4s gate✅)·load .29=27.08/.12=26.22✅(无pc2_fast)·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3106（2026-11-23 06:15, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291780/700000(41.69%) step_avg(last10)=7238ms(<7.4s gate✅)·load .29=23.18/.12=27.59✅(无pc2_fast)·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3105（2026-11-23 06:09, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291730 step_avg(last10)=7190ms(<7.4s gate✅)·load .29=25.52/.12=25.83✅(无pc2_fast)·daemon idle等292k ETA≈06:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3102（2026-11-23 05:47, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291530/700000(41.65%) step_avg(last10)=7206ms(<7.4s gate✅)·load .29=24.70/.12=28.08✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3101（2026-11-23 05:39, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291470/700000(41.64%) step_avg(last10)=7216ms(<7.4s gate✅)·load .29=28.44/.12=25.01✅(无pc2_fast)·daemon idle等292k ETA≈06:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3100（2026-11-23 05:30, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291400/700000(41.63%) step_avg(last10)=7143ms(<7.4s gate✅)·load .29=27.27/.12=26.59✅(无pc2_fast)·daemon idle等292k ETA≈06:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3074–#3096（2026-11-23 01:59–05:04, 放行autoqueue令·监控巡检轮23条·backlog全清270k-290k 11ckpt·训练健康step~7.0-7.4s(NOT elevated✅)·load正常·daemon idle等290k/292k·290k于02:46起eval,04:03 DONE harness_avg=55.25%）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3073（2026-11-23 01:51, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289580 step_avg≈7126ms(NOT elevated✅)·load .29=25.66/.12=26.50✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3072（2026-11-23 01:46, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289530 step_avg≈7095ms(NOT elevated✅)·load .29=27.71/.12=23.55✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3071（2026-11-23 01:38, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289470 step_avg≈7081ms(NOT elevated✅)·load .29=26.99/.12=28.41✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3070（2026-11-23 01:30, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289400 step_avg≈7103ms(NOT elevated✅)·load .29=26.99/.12=23.72✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3069（2026-11-23 01:18, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289290 step_avg≈7247ms(NOT elevated✅)·load .29=25.39/.12=23.11✅·daemon idle等290k ETA~02:44）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3068（2026-11-23 01:08, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289210 step_avg≈7396ms(NOT elevated✅)·load .29=26.33/.12=25.20✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3067（2026-11-23 01:02, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289160 step_avg≈7362ms(NOT elevated✅)·load .29=26.72/.12=25.44✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3066（2026-11-23 00:56, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289110 step_avg≈7172ms(NOT elevated✅)·load .29=27.68/.12=27.21✅·daemon idle等290k ETA~02:40）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3065（2026-11-23 00:49, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289060 step_avg≈7346ms(NOT elevated✅)·load .29=26.21/.12=27.10✅·daemon idle等290k ETA~02:44）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3064（2026-11-23 00:41, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288990 step_avg≈7130ms(NOT elevated✅)·load .29=27.40/.12=26.44✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3063（2026-11-23 00:37, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288960 step_avg≈7210ms(NOT elevated✅)·load .29=24.73/.12=24.62✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3062（2026-11-23 00:34, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288930 step_avg≈7180ms(NOT elevated✅)·load .29=27.64/.12=26.51✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3061（2026-11-23 00:28, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=288880 step_avg=7250ms(NOT elevated✅)·load .29=28.33/.12=正常✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3060（2026-11-23 00:20, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288810 step_avg=7288ms(NOT elevated✅)·load .29=26.76/.12=23.13✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3047–#3057（2026-11-22 22:31–23:56, 放行autoqueue令·288k eval RUNNING监控轮11条·backlog全清270k-286k·训练健康step~7.1-7.3s·load正常·daemon eval 288k·288k于00:04 DONE harness_avg=58.50%）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2990–#3034（已归档，含 #3030 286k eval DONE·#3029-#2990 286k/284k/282k eval RUNNING监控轮）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2989及更早（已归档，含 #2977-#2989 监控轮 + #2900–#2976 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

WAITING: 0(✅ 2026-11-23 17:23 #3170 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=297280/700000(42.47%) step7.12s(baseline,无eval,0/15>7.4s✅)·loss≈1.99 0NaN/0skip✅·step-time无eval负载baseline=7.12s<7.4s gate✅·load .29=24.63/.12=24.06✅·daemon alive(PID1081392,idle等298k ETA~18:49)·backlog 270k-296k全清15ckpt(directive#1✅维持)·296k=59.12%DONE·298k NOT on disk(ETA~18:49)·纯监控未碰训练进程(铁律悍守))

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