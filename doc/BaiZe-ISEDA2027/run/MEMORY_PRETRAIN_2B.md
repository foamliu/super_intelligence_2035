step time 已恢复（#3379 的 >7.4s spike 于 320810 起回落，最近 10 步 avg=7.22s all<7.4s✅）。根因=harness CPU 争抢（NOT eval），已自愈。320k eval DONE。autoqueue 52/52ckpt✅。daemon idle 等 322k（lands~19:15）。报告 40882B(52/52ckpt)✅。WAITING=0。

> #3379（2026-11-25 16:40, ⚠️step time 异常+320k eval DONE·320k harness_avg=54.62%(arc_c31/arc_e64/boolq41/hella51/obqa33/piqa78/sciq80/wino59)·autoqueue令持续履行(52/52ckpt 10k-320k✅)·daemon idle等322k(lands~19:20)·报告40882B(52/52ckpt)·⚠️step time持续>7.4s:320680=7.64s→320690=7.98s→320700=7.44s(3连续步)·根因=harness SWE-bench CPU争抢(.29上5+opencode/bun进程~500%CPU:opencode PrismJS 143%+django test 93%+mocha 57%+opencode 38.6%+npm 37.7%+kcompactd0/1 58%)+NOT eval-caused(daemon idle无llama-server)·训练iter=320700/700000(45.81%) loss=1.988 0NaN/0skip✅·lr=1e-3·grad norm=0.105✅·train.sh PID2547367✅(5d2h+)·GPU 8×94-100%✅·load .29=24.20/26.57/28.09(1min<15min,趋势下降但step仍高)·per11-20令:step偏离~7s→⚠️待运维处理+WAITING=1·per11-21令:eval通道无异常(320k已DONE)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter=320700@16:39:48) daemon=/tmp/baize_l1_autoqueue_continuous.log(320000 DONE@16:35:24,idle@16:35:55) ckpt=.../checkpoints/iter_0320000 results=.../lm_eval_results/gguf_iter_320000_fixed_8set/results.json(25998B) report=.../reports/report_pretrain_llamacpp_scaling_zh.html(40882B,52/52ckpt)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·体积MEMORY≈31.5KB<32KB✅ TASK≈30.6KB<32KB✅）→ daily-memories/2026-11-25.md
> #3380（2026-11-25 17:08, 监控巡检+step time 恢复确认+报告修复·step time 已恢复:最近10步(320840-320930)avg=7223ms(7.22s,0/10>7.4s✅),#3379的spike(320680-320750,7.64-8.14s)已过·autoqueue令持续履行(52/52ckpt 10k-320k✅)·daemon idle等322k(lands~19:15)·报告修复:regen 28986B→40882B(52/52ckpt,此前被revert为旧26pts版)·训练iter=320930/700000(45.85%) loss=1.993 0NaN/0skip✅·lr=1e-3·grad norm=0.095-0.122✅(320920单点spike 1.076→0.122已恢复)·train.sh PID2547367✅(5d2h+)·GPU 8×94-100%✅·load .29=26.79/26.09/26.60·harness进程仍在(opencode 25.9%+bun 27.5%+cline-hub 22.8%+kcompactd 21.9%)但step已恢复·per11-20令:step已恢复→WAITING=0·per11-21令:eval通道无异常·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter=320930@17:06:50) daemon=/tmp/baize_l1_autoqueue_continuous.log(idle@17:00:58) report=.../reports/report_pretrain_llamacpp_scaling_zh.html(40882B,52/52ckpt)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·体积MEMORY≈30KB<32KB✅ TASK≈30.6KB<32KB✅）→ daily-memories/2026-11-25.md


> 📦 #3376-#3378（2026-11-25 16:02-16:32, 监控巡检3轮·320k eval RUNNING→DONE·step正常(7.20-7.26s,0>7.4s✅)·eval未拖训练✅·报告修复(regen→40400B 51/51ckpt)）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3375（2026-11-25 15:45, 监控巡检·320k eval RUNNING·step7.25s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3374（2026-11-25 15:33, 监控巡检+报告修复·320k eval RUNNING·报告修复(vision auto-commit revert→regen 51/51ckpt 40400B✅)·step7.24s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3373（2026-11-25 15:20, 监控巡检·320k eval RUNNING·step7.22s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3372（2026-11-25 15:10, 监控巡检·daemon idle·autoqueue令持续履行(51/51ckpt 10k-318k✅)·训练iter=319950/700000(45.7%) step_avg(recent8)=7238ms(7.24s,0/8>7.4s✅ fully recovered)·loss=2.006 0NaN/0skip✅·lr=1e-3·grad norm=0.099✅·train.sh PID2547367✅(5d0h+,etimes=433570s)·daemon(PID1081392)idle sleep300s waiting 320k·step-time normal NOT eval-caused(daemon idle无llama-server)·GPU all 8×100%✅·load .29=27.89/28.33/28.13 .12=23.19/24.45/25.05·320k NOT on disk(50steps×7.2s≈6min→lands~15:16)·report=40400B(51/51ckpt)✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3371（2026-11-25 15:01, 监控巡检+报告修复·daemon idle·autoqueue令持续履行(51/51ckpt)·训练iter=319880 step7.26s recovering·报告修复(vision auto-commit merge conflict markers→regen 51/51ckpt 40400B✅)·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3370（2026-11-25 14:40, 监控巡检·daemon idle·step_avg=8.53s re-elevated(NOT eval-caused,harness CPU)·report=53258B(51/51ckpt)·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3369（2026-11-25 14:27, 监控巡检·step7.42s recovering(non-eval-caused,harness CPU)·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3367（2026-11-25 13:57, 监控巡检·autoqueue令完全履行(270k=59.75%/272k=56.75%/51ckpt done)·step-time elevated NOT eval-caused(harness CPU contention)·WAITING=0·归档#3366/#3356-3358）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 §#3359–#3366（2026-11-25 12:32–13:47, 监控巡检8轮·316k eval DONE harness=57.38%/318k eval DONE harness=56.25%·daemon print口径已修(acc_only→harness_avg #3365)·训练健康step~7.15-7.34s·backlog51/51ckpt(10k-318k)·eval未拖训练✅）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3354-#3355（2026-11-25 11:35-11:50, 监控巡检2轮·316k eval RUNNING·训练iter318230-318360 step7.27-7.31s·step-time Δ+0.10~0.14s NOT elevated✅·backlog49/49清·report stale 28986B(未发现)→已修复见#3356）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3352-#3353（2026-11-25 11:11-11:19, 放行autoqueue令·监控巡检2轮·316k eval RUNNING/314k eval DONE=56.25%·训练健康step7.27-7.32s·step-time Δ+0.10~0.15s NOT elevated✅·backlog49/49清·eval未拖训练✅）→ daily-memories/2026-11-25.md；需要时再读。


> 📦 #3351（2026-11-25 11:01, 监控巡检·314k eval RUNNING(~72min)·训练iter=317940 step7.29s·backlog48/48ckpt·report=38961B(48/48ckpt)）→ daily-memories/2026-11-25.md；需要时再读。

> #3349（2026-11-25 10:42, **🔴L1下降排查完成·判定：NOT真下降**·根因=口径混淆(acc_only vs harness_avg)+limit=100统计噪声·314k eval RUNNING·训练iter=317800/700000(45.4%)·step_avg(recent5)=7.26s✅·loss≈1.99 0NaN/0skip✅·lr=1e-3·grad norm正常(0.088-0.102)·train.sh PID2547367✅·daemon(PID1081392)active eval 314k·llama-server PID1861195(-t4,nice19,port8201)·**L1排查5项结论**：①口径全一致(48/48ckpt n=8/8 harness+acc_only)✅ ②报告HTML 312k=55.62%(harness) vs daemon log 52.75%(acc_only)→非真矛盾,是两种指标;daemon内联print(lines183-190)用acc_only非harness,导致log数字偏低~2.9pp ③GGUF脚本git diff(2906b2b3c7..2ab01fc98c)空=未改✅ ④llama.cpp二进制Nov5 md5=f95ac95215a7e61a534eccba9a4ed49d=全程一致✅ ⑤训练loss 260k-314k≈1.99-2.03平坦无异常,grad norm偶发spike(0.442/2.293)均次步恢复✅·**统计判定**：pre-270k均值=56.72%(26pts,min51.50,max60.12) vs post-270k均值=58.30%(22pts,min55.25,max60.63)=**+1.57pp(更高非更低)**;末4点(306k-312k:59.25/58.38/56.88/55.62)均值57.53%仍>pre-270k均值;limit=100→逐集stderr±4.5%→Avg stderr±1.6%,波动55-61%全在噪声带内·**报告已重生成48/48ckpt 38961B**(此前10:27被覆盖为26pts/28986B,仅10k-260k)·⚠️daemon内联print脚本待停时修(不影响results.json/报告)·per11-20令不干预训练 per11-21令WAITING=0·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter317800@10:41:12) daemon=/tmp/baize_l1_autoqueue_continuous.log·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯排查未碰train.sh/configs/.bak/训练进程·体积MEMORY≈27KB<32KB✅）→ daily-memories/2026-11-25.md

> 📦 #3348（2026-11-25 10:29, 放行autoqueue令·监控巡检·314k eval RUNNING(~41min)·训练iter=317700 step7.50s(non-eval-caused uptick)·loss≈1.99·backlog48/48清·270k=59.75%/272k=56.75%·312k=55.62%·report=38961B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3347（2026-11-25 10:17, 放行autoqueue令·监控巡检·314k eval RUNNING(~28min)·训练iter=317600 step_avg(recent5)=7.26s✅·eval未拖训练Δ-0.05s✅·backlog48/48清·report=38961B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3346（2026-11-25 10:05, 放行autoqueue令·监控巡检·314k eval RUNNING(~16min)·训练iter=317500 step_avg(recent5)=7.28s✅·eval未拖训练Δ-0.03s✅·backlog48/48清·270k=59.75%/272k=56.75%·report=38961B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3345（2026-11-25 09:58, 放行autoqueue令·监控巡检·314k eval RUNNING(~9min)·训练iter=317450 step_avg(recent5)=7.31s✅·eval未拖训练Δ+0.05s✅·backlog48/48清·270k=59.75%/272k=56.75%·report=38961B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3344（2026-11-25 09:49, 放行autoqueue令·监控巡检·312k eval DONE=55.62%·314k eval RUNNING(HF export phase)·训练iter=317340 step_avg(recent15)=7.29s(4/15>7.4s非持续✅)·eval未拖训练Δ+0.01s✅·backlog 270k-312k全清48/48ckpt✅·report=38961B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3343（2026-11-25 09:28, 放行autoqueue令·监控巡检·312k eval RUNNING(~56min)·训练iter=317200 step_avg(recent15)=7.33s(brief uptick 7553-7585ms@317170-317190已回落✅)·eval未拖训练Δ+0.05s✅·backlog47/47清·270k=59.75%/272k=56.75%·report=38438B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3342（2026-11-25 09:17, 放行autoqueue令·监控巡检·312k eval RUNNING(~44min)·训练iter=317100 step_avg(recent5)=7.25s(0/5>7.4s✅)·eval未拖训练Δ-0.03s✅·backlog47/47清·270k=59.75%/272k=56.75%·report=38438B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3341（2026-11-25 09:06, 放行autoqueue令·监控巡检·312k eval RUNNING(~33min)·训练iter=317020 step7.36s(2/5>7.4s非持续✅,last2下降✅)·eval未拖训练Δ+0.08s✅·backlog47/47清·270k=59.75%/272k=56.75%·report=38438B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3340（2026-11-25 08:56, 放行autoqueue令·监控巡检·312k eval RUNNING(~24min)·训练iter=316940 step7.32s·eval未拖训练Δ+0.04s✅·backlog47/47清·270k=59.75%/272k=56.75%·report=38438B）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3339（2026-11-25 08:43, 放行autoqueue令·监控巡检·312k eval RUNNING(~11min)·⚠️daemon stuck on 312k 23:13→08:32(~9h):`01_convert_hf_to_gguf.sh` missing(git untrack commit `931cc40e30`)→recovered at 08:32,GGUF done,eval started·训练iter=316840 step7.32s·backlog47/47清·270k=59.75%/272k=56.75%·report regenerated 38438B·MEMORY/daily-memories/report re-tracked to git）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3338（2026-11-24 19:15, 监控巡检·310k eval RUNNING(~18min)·训练iter=310160 step7.02s·backlog46/46清·308k=58.38% latest·step-time pre7.23→during7.02s Δ-0.21s✅）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3337（2026-11-24 19:06, 监控巡检·310k eval RUNNING(~9min)·⚠️step_avg(recent9)=7453ms last3>7.4s(non-eval-caused,自回落见#3338)·backlog46/46清）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3336（2026-11-24 18:59, 监控巡检·310k eval RUNNING(daemon auto-pick@18:55,GGUF done@18:57,lm_eval started)·训练iter=310040 step_avg(recent8)=7.29s(1/8>7.4s✅非持续)·loss≈2.00 0NaN/0skip✅·load .29=26.16✅·step-time三段:pre7.23→during7.29s Δ+0.06s✅<7.4s·eval未拖训练✅·backlog46/46✅）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3335（2026-11-24 18:53, 监控巡检·daemon idle无eval负载·训练健康iter=309990 step7.29s·backlog46/46清·310k ETA~18:55）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3331–#3334（2026-11-24 18:26–18:45, 放行autoqueue令·监控巡检4轮·daemon idle无eval负载·训练健康iter309750-309920 step7.27-7.34s(all avg<7.4s✅)·backlog46/46清·308k=58.38% latest·daemon idle等310k）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3330（2026-11-24 18:09, 监控巡检·daemon idle·训练iter=309620 step7.34s·backlog46/46清·修复vision auto-commit覆盖report问题(stale 28986B→恢复37957B)·per11-20令记录不干预 per11-21令WAITING=0）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3329（2026-11-24 18:01, 监控巡检·daemon idle·✅step-time恢复~7.3s(前轮7.85-8.57s已自行回落,非eval引起)·训练iter=309550 step7.36s·backlog46/46清 308k=58.38% daemon idle等310k(~18:50)·per11-20令记录不干预 per11-21令WAITING=0）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3328（2026-11-24 17:50, 监控巡检·⚠️step-time 7.85-8.57s非eval引起(daemon idle)·训练iter=309470·backlog46/46清·step-time已于此轮后回落至7.3s见#3329）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3316–#3325（2026-11-24 16:11–17:20, 放行autoqueue令·监控巡检10轮·daemon idle无eval负载·训练健康iter308680-309230 step7.14-7.51s(16:11-16:43<7.4s✅,16:55起⚠️>7.4s非eval引起)·308k eval DONE=58.38%(@16:10,daemon auto-pick)·backlog46/46清·L1报告46/46ckpt@37957B✅·eval未拖训练(pre7.23→during7.18→post7.14-7.51 Δ≤0✅)·daemon idle等310k(~18:49-18:57)·per11-20令记录不干预 per11-21令WAITING=0）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3315（2026-11-24 16:06, 放行autoqueue令·监控巡检·308k eval RUNNING(~73min in)·训练健康iter=308630 step7.18s·eval未拖训练✅·backlog 45/45ckpt）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3304–#3314（2026-11-24 14:26–16:00, 放行autoqueue令·监控巡检11轮·308k eval RUNNING全程监控(iter308050→308590 step7.10-7.19s all<7.4s✅)·eval未拖训练(pre7.23→during7.10-7.19s Δ-0.04~-0.13s✅)·backlog全清45/45ckpt·daemon idle→eval 308k交替·load正常）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3290–#3303（2026-11-24 12:39–14:15, 放行autoqueue令·监控巡检14轮·daemon idle无eval负载·训练健康iter306910-307710 step7.09-7.24s(all<7.4s✅)·load .29=21.94-28.98(1m)✅·backlog全清45/45ckpt✅·eval未拖训练✅）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3281–#3289（2026-11-24 11:43–12:34, 放行autoqueue令·306k eval RUNNING→DONE(59.25%@12:16)监控+daemon idle监控~9轮·训练健康iter306440-306850 step7.09-7.26s(all<7.4s✅)·load正常·step-time pre7.23s→during7.09-7.11s→post7.12-7.14s eval未拖训练✅·backlog 270k-306k全清45/45ckpt✅·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告45/45ckpt@37483B✅）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3280（2026-11-24 11:36, 放行autoqueue令·监控巡检·306k eval RUNNING(~39min in)·训练健康iter=306380 step_avg(recent2)=7.20s·load .29=25.88(1m)✅·eval未拖训练✅·backlog 270k-304k全清44/44ckpt）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3267-#3279（2026-11-24 10:07-11:28, 放行autoqueue令·监控巡检~13轮·306k ckpt LANDED@10:50→daemon auto-pick eval@10:57·306k eval RUNNING全程监控·训练健康iter305640→306310 step~7.09-7.63s(pytest争抢@10:07-10:45已恢复,306k eval期间7.09-7.50s NOT elevated✅)·backlog 270k-304k全清44/44ckpt·270k=59.75%/272k=56.75%(积压点已补评✅)·含#3273 306k LANDED/#3267 pytest恢复/WAITING→0）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3266（2026-11-24 09:45, 放行autoqueue令·监控巡检·⚠️step time 15avg=7.46s>7.4s gate·根因=pytest(harness)CPU争抢非eval·**已自愈(见#3267)**）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3265（2026-11-24 09:29, 放行autoqueue令·监控巡检·daemon idle无eval负载·训练健康iter=305340/700000(43.62%) step_avg(recent15)=7265ms(7.26s,7021-7451,1/15>7.4s✅非持续spike)·loss≈1.97-1.99(1.970624-1.990572) 0NaN/0skip✅·lr=1e-3 grad norm0.083-0.126✅·load(directive#2 daemon idle无eval) .29=36.85(1m)✅ .12=26.17(1m)✅·step-time(directive#3)no-eval baseline(#3247 06:47)=7.23s→daemon-idle now(recent15)=7.26s Δ+0.03s NOT elevated✅<7.4s gate(1/15>7.4s非持续)·backlog 270k-304k全清44/44ckpt(directive#1✅维持)·304k=59.00%(latest done,08:10:31)·270k=59.75%/272k=56.75%(11-21令积压点已补评✅)·L1报告44/44ckpt@08:18(37018B,harness口径✅,daemon自动刷新)·daemon idle(PID1081392 etimes~61.5h)sleep300s等306k(latest ckpt=iter_0304000,训练@305340,lands~10:48,daemon auto-pick)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter305340@09:28:14) daemon=/tmp/baize_l1_autoqueue_continuous.log([idle]@09:26:09) ckpt=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints(latest iter_0304000) results=.../lm_eval_results/gguf_iter_304000_fixed_8set/results.json report=run/reports/report_pretrain_llamacpp_scaling_zh.html(44/44ckpt,37018B@08:18)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈26.5KB<32KB✅ TASK≈25.3KB<32KB✅）→ daily-memories/2026-11-24.md

> 📦 #3264（2026-11-24 09:22, 放行autoqueue令·监控巡检·daemon idle·训练健康iter=305280 step7.24s(0/15>7.4s✅)·load .29=29.06 .12=27.77✅·step no-eval7.23s→idle7.24s Δ+0.01s✅·backlog 270k-304k全清44/44ckpt·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告44/44ckpt@08:18·daemon idle等306k(lands~10:48)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3257–#3263（2026-11-24 08:25–09:15, 放行autoqueue令·监控巡检7轮·daemon idle无eval负载·训练健康iter304810-305230 step7.15-7.24s(all<7.4s✅)·loss≈1.97-1.99 0NaN/0skip✅·load正常·backlog 270k-304k全清44/44ckpt✅·304k=59.00%·270k=59.75%/272k=56.75%(积压点已补评✅)·L1报告44/44ckpt@08:18✅·daemon idle等306k(lands~10:48)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 #3256（2026-11-24 08:12, 放行autoqueue令·304k eval DONE✅ harness-avg=59.00%·训练健康iter=304700 step7.22s·backlog 270k-304k全清44/44ckpt·302k=59.13%/270k=59.75%/272k=56.75%·L1报告44/44ckpt@37018B）→ daily-memories/2026-11-24.md；需要时再读。
> 📦 #3255（2026-11-24 07:59, 放行autoqueue令·304k eval RUNNING(~67min in,ETA~08:08-13)·训练健康iter=304600 step7.22s·backlog 43/43ckpt·302k=59.13%·L1报呃43/43ckpt@36561B）→ daily-memories/2026-11-24.md；需要时再读。



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
 