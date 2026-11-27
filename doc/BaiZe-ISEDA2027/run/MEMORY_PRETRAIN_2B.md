🟢 监控巡检·训练健康iter=341790/700000(48.83%) loss≈1.975-1.994 step avg10=7330ms=7.33s(✅below 7.4s gate·stable·daemon idle·GPU 8×100%)·S2切换ALL READY(10-point✅ re-verified this round)·latest ckpt=340000·350k ETA~05:00 on 11-28·eval_next=350k(=S2切换点)·WAITING=0
> #3490（2026-11-27 12:15, 监控巡检·训练健康iter=341790/700000(48.83%) step avg10=7330ms=7.33s(✅below 7.4s gate·stable·daemon idle·GPU 8×100%)·S2切换ALL READY(10-point re-verified this round)·latest ckpt=340000·350k ETA~05:00 on 11-28·
> 训练健康iter=341790/700000(48.83%) loss≈1.975-1.994(lr=1e-3,grad norm 0.089-0.125✅,0NaN/0skip✅)·step avg10=7330ms=7.33s(✅BELOW 7.4s gate·stable)·latest10:7350/7423/7220/7435/7295/7394/7341/7288/7352/7163ms·all<7.5s✅·GPU .29 8×100%/74501-74959MiB✅·load .29=26.98/25.74/25.75(224cores)·
> **step avg10=7.33s STABLE**:all last 10 steps<7.5s✅·NON-eval-caused(daemon idle,no llama-server)·autoqueue gate(step<7.4s)PASS→350k eval will proceed·
> **daemon idle**:autoqueue PID501728 alive(etimes~56500s≈15.7h),no llama-server running·340k eval DONE(harness_avg=60.13%)·next eval=350k(10k boundary=S2切换点)·report 43506B/66ckpt·10k cadence✅(L99:iter%10000==0)·
> **S2切换ALL READY(10-point✅ re-verified this round)**:①shim 4226B✅(ls /nas_train/app.e0031982/code/BaiZe-ISEDA2027/)②train.sh L206 BLEND_CURSOR_OFFSETS_JSON passthrough✅(grep)③pretrain_launcher.py L306 shim import✅(grep)④cursor_offsets_350k.json 1093B✅(7 shared+5 new sources,89.6M consumed)⑤blend_s2_preblend.tsv 3625B✅(ls code/baize-llm/configs/)⑥s2_blend_switch_config.json 1298B✅⑦bridge 10/10✅⑧standalone 8/8✅⑨integration 7/7✅⑩SWITCH_RUNBOOK.md 187lines 9节✅·s1.env BLEND_TSV=blend_s1_preblend.tsv✅(current S1,switch to S2 at 350k)·
> **350k ETA**:iter=341790,remaining=8210 steps×7.33s≈60179s≈16.7h→~05:00 on 11-28·350k=eval+切换:先切换(冷切换~10min)后eval(CPU-only~76min,与S2训练并行)·latest ckpt=iter_0340000✅(BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/)·
> **未碰训练/configs/.bak/daemon**(维护态铁律悍守)·evidence:worker_log tail(iter341790@12:15)·nvidia-smi 8×100%·ps daemon idle(PID501728)·10-point ls/grep all✅·MEMORY≈30KB<32KB✅）
> #3489（2026-11-27 12:00, 监控巡检·训练健康iter=341650/700000(48.81%) step avg10=7332ms=7.33s(✅below 7.4s gate·stable·daemon idle)·S2切换ALL READY(10-point re-verified this round)·latest ckpt=340000·350k ETA~05:00 on 11-28·
> 训练健康iter=341650/700000(48.81%) loss≈1.979-1.994(lr=1e-3,grad norm 0.086-0.116✅,0NaN/0skip✅)·step avg10=7332ms=7.33s(✅BELOW 7.4s gate·stable)·latest10:7322/7354/7488/7227/7353/7356/7229/7350/7423/7220ms·all<7.5s✅·GPU .29 8×91-100%/74501-74959MiB✅·load .29=27.23/26.10/26.04(224cores)·
> **step avg10=7.33s STABLE**:continued recovery from 11-26 oscillation·all last 10 steps<7.5s✅·NON-eval-caused(daemon idle)·autoqueue gate(step<7.4s)PASS→350k eval will proceed·
> **daemon idle**:autoqueue PID501728 alive(etimes~55251s≈15.3h),no llama-server running·340k eval DONE(harness_avg=60.13%)·next eval=350k(10k boundary=S2切换点)·10k cadence✅(L99:iter%10000==0)·
> **S2切换ALL READY(10-point✅ re-verified this round)**:①shim 4226B✅(ls)②train.sh L206 BLEND_CURSOR_OFFSETS_JSON passthrough✅(grep)③pretrain_launcher.py L306 shim import✅(grep)④cursor_offsets_350k.json 1093B✅⑤blend_s2_preblend.tsv 3625B✅(ls)⑥s2_blend_switch_config.json 1298B✅⑦bridge 10/10✅⑧standalone 8/8✅⑨integration 7/7✅⑩SWITCH_RUNBOOK.md 187lines✅·s1.env BLEND_TSV=blend_s1_preblend.tsv✅(current S1)·
> **350k ETA**:iter=341650,remaining=8350 steps×7.33s≈61206s≈17.0h→~05:00 on 11-28·350k=eval+切换:先切换(冷切换~10min)后eval(CPU-only~76min)·latest ckpt=iter_0340000✅(nemo_experiments/baize2b/checkpoints/)·
> **未碰训练/configs/.bak/daemon**(维护态铁律悍守)·evidence:worker_log tail(iter341650@11:58)·nvidia-smi 8×91-100%·ps daemon idle(PID501728)·10-point ls/grep all✅·MEMORY≈29KB<32KB✅）

> #3487（2026-11-27 11:35, 监控巡检·训练健康iter=341450/700000(48.78%) step avg10=7711ms=7.71s(⚠️ELEVATED above 7.4s gate·NON-eval-caused·daemon idle·last step=8182ms spike)·S2切换ALL READY(10-point re-verified this round)·latest ckpt=340000·350k ETA~05:54 on 11-28·
> 训练健康iter=341450/700000(48.78%) loss≈1.977-1.994(lr=1e-3,grad norm 0.084-0.107✅,0NaN/0skip✅)·step avg10=7711ms=7.71s(⚠️ABOVE 7.4s gate)·latest10:7615/7551/7402/7632/7634/7593/7666/7967/7868/8182ms·last step 8182ms=spike(highest in last10)·GPU .29 8×96-100%/74501-74959MiB✅·load .29=25.67/25.91/26.36(224cores)·
> **step avg10=7.71s ELEVATED**:NON-eval-caused(daemon idle,no llama-server)·oscillating pattern since 11-26 night(7.27↔7.90↔7.27↔7.58↔7.81↔7.71)·last step=8182ms spike→concerning but NOT yet at ⚠️ threshold(avg10 persistently>8.0s for>2h)·autoqueue gate(step<7.4s)will hold 350k eval if still elevated·S2 switch NOT affected by step gate·
> **daemon idle**:autoqueue PID501728 alive(etimes~53800s≈14.9h),no llama-server running·340k eval DONE(harness_avg=60.13%)·next eval=350k(10k boundary=S2切换点)·report 43506B/66ckpt·10k cadence✅·
> **S2切换ALL READY(10-point✅ re-verified this round)**:①shim blend_hot_switch_bridge_compat.py 4226B✅(ls 11:35)②train.sh L202/L206 BLEND_CURSOR_OFFSETS_JSON透传✅(grep)③pretrain_launcher.py L306 shim import✅(grep)④cursor_offsets_350k.json 1093B✅⑤blend_s2_preblend.tsv 3625B✅(ls)⑥s2_blend_switch_config.json✅⑦bridge 10/10✅⑧standalone 8/8✅⑨integration 7/7✅⑩SWITCH_RUNBOOK.md 9节✅·
> **350k ETA**:iter=341450,remaining=8550 steps×7.71s≈65920s≈18.3h→~05:54 on 11-28·350k=eval+切换:先切换(冷切换~10min)后eval(CPU-only~76min,与S2训练并行)·latest ckpt=iter_0340000✅(nemo_experiments/baize2b/checkpoints/)·
> **未碰训练/configs/.bak/daemon**(维护态铁律悍守)·evidence:worker_log tail-30(iter341450@11:34)·nvidia-smi 8×96-100%·ps daemon idle·shim ls 4226B✅·pretrain_launcher.py grep L306✅·train.sh grep L202/L206✅·blend_s2_preblend.tsv ls 3625B✅·latest ckpt=340000✅·MEMORY≈24KB<32KB✅）
> #3486（2026-11-27 11:26, 监控巡检·训练健康iter=341380/700000(48.77%) step avg10=7808ms=7.81s(⚠️ELEVATED above 7.4s gate·NON-eval-caused·daemon idle·oscillating)·S2切换ALL READY(10-point re-verified this round)·latest ckpt=340000·350k ETA~06:00 on 11-28·
> 训练健康iter=341380/700000(48.77%) loss≈1.977-1.994(lr=1e-3,grad norm 0.086-0.117✅,0NaN/0skip✅)·step avg10=7808ms=7.81s(⚠️ABOVE 7.4s gate)·latest10:8006/7904/7631/8019/7780/7665/8502/7615/7551/7402ms·3 spikes>8s(341290=8006/341320=8019/341350=8502)·last 3 steps trending down(7615→7551→7402)→may be recovering·GPU .29 8×92-100%/74501-74959MiB✅·load .29=27.04/26.62/26.60(224cores)·load .12=25.83/25.70/25.63·
> **step avg10=7.81s ELEVATED**:NON-eval-caused(daemon idle,no llama-server)·oscillating pattern since 11-26 night(7.27↔7.90↔7.27↔7.58↔7.81)·last 3 steps trending down→may be recovering·NOT marking⚠️yet(will if avg10 persistently>8.0s for>2h)·autoqueue gate(step<7.4s)will hold 350k eval if still elevated·S2 switch NOT affected by step gate·
> **daemon idle**:autoqueue PID501728 alive(etimes~53200s≈14.8h),no llama-server running·340k eval DONE(harness_avg=60.13%)·next eval=350k(10k boundary=S2切换点)·report 43506B/66ckpt·10k cadence✅·
> **S2切换ALL READY(10-point✅ re-verified this round)**:①shim blend_hot_switch_bridge_compat.py 4226B✅(ls+cat,monkey-patch BlendedDataset._build_indices)②train.sh L203-207 BLEND_CURSOR_OFFSETS_JSON透传✅(grep)③pretrain_launcher.py L303-307 shim import✅(grep)④cursor_offsets_350k.json 1093B✅(cat,89.6M total consumed,7 shared+5 new sources)⑤blend_s2_preblend.tsv 3625B✅(ls)⑥s2_blend_switch_config.json✅⑦bridge 10/10✅(verify_results_bridge.json all PASS)⑧standalone 8/8✅⑨integration 7/7✅⑩S2_SWITCH_RUNBOOK.md 7570B 9节✅(read full,comprehensive)·
> **350k ETA**:iter=341380,remaining=8620 steps×7.81s≈67362s≈18.7h→~06:06 on 11-28·350k=eval+切换:先切换(冷切换~10min)后eval(CPU-only~76min,与S2训练并行)·latest ckpt=iter_0340000✅(baize2b/checkpoints/)·
> **未碰训练/configs/.bak/daemon**(维护态铁律悍守)·evidence:worker_log tail-30(iter341380@11:25)·nvidia-smi 8×92-100%·ps daemon idle·shim ls+cat 4226B✅·pretrain_launcher.py grep L303-307✅·train.sh grep L203-207✅·cursor_offsets_350k.json cat✅·verify_results_bridge.json cat 10/10✅·S2_SWITCH_RUNBOOK read 7570B✅·latest ckpt=340000✅·MEMORY≈22KB<32KB✅）
> #3485（2026-11-27 11:17, 监控巡检·训练健康iter=341320/700000(48.76%) step avg10=7581ms=7.58s(⚠️ELEVATED above 7.4s gate·NON-eval-caused·daemon idle)·S2切换ALL READY·350k ETA~05:35 on 11-28·
> 训练健康iter=341320/700000(48.76%) loss≈1.980-2.005(lr=1e-3,grad norm 0.086-0.113✅,0NaN/0skip✅)·step avg10=7581ms=7.58s(⚠️ABOVE 7.4s gate)·latest10:7307/7400/7346/7349/7304/7542/8006/7904/7631/8019ms·3 spikes>7.9s in last 5(341290=8006/341300=7904/341320=8019)·load .12=25.32/25.88/26.53(224cores)·
> **step avg10=7.58s ELEVATED**:NON-eval-caused(daemon idle,no llama-server)·was 7.27s at 11:07(#3484)·similar pattern as #3473(08:22 avg10=7.90s→recovered to 7.27s)·monitoring,NOT marking⚠️yet(will if persists>2h)·autoqueue gate(step<7.4s)will hold eval if still elevated when 350k lands·
> **daemon idle**:autoqueue PID501728 alive(etimes~52700s≈14.6h),no llama-server running·340k eval DONE(harness_avg=60.13%,see #3483)·next eval=350k(10k boundary=S2切换点)·report 43506B/66ckpt·10k cadence✅(L96-99 iter%10000==0)·
> **S2切换ALL READY(10-point✅)**:①shim 4226B✅(ls)②train.sh L206 BLEND_CURSOR_OFFSETS_JSON透传✅(grep)③pretrain_launcher.py L306 shim import✅(grep)④cursor_offsets_350k.json✅⑤blend_s2_preblend.tsv✅⑥s2_blend_switch_config.json✅⑦bridge 10/10✅⑧standalone 8/8✅⑨integration 7/7✅⑩SWITCH_RUNBOOK.md 9节✅·
> **350k ETA**:iter=341320,remaining=8680 steps×7.58s≈65794s≈18.3h→~05:35 on 11-28·350k=eval+切换:先切换(冷切换~10min)后eval(CPU-only~76min,与S2训练并行)·
> **未碰训练/configs/.bak/daemon**(维护态铁律悍守)·evidence:worker_log tail-15(iter341320@11:16)·ps daemon idle·autoqueue log tail(idle)·train.sh grep L206✅·shim ls 4226B✅·pretrain_launcher.py grep L306✅·latest ckpt=340000✅·MEMORY≈20KB<32KB✅）
> #3484（2026-11-27 11:0x, 监控巡检·训练健康iter=341240/700000(48.75%) step avg10=7270ms=7.27s(✅below 7.4s gate)·S2切换10-point ALL VERIFIED reconfirmed·daemon idle waiting 350k·350k ETA~04:49 on 11-28·
> 训练健康iter=341240/700000(48.75%) loss≈1.979-1.993(lr=1e-3,grad norm 0.086-0.117✅,0NaN/0skip✅)·step avg10=7270ms=7.27s(✅BELOW 7.4s gate)·latest10:7286/7389/7583/7481/7152/7279/7272/7466/7194/7231ms·GPU .29 8×95-100%/74501-74959MiB/74.5GB✅·load .29=26.18/26.47/27.08(224cores)·load .12=26.71/25.82/25.75·.12 pretrain_launcher PID1439817 alive(etimes=592011s≈6.85d)·
> **daemon idle**:autoqueue PID501728 alive(etimes~52200s≈14.5h),no llama-server/lm_eval running·340k eval DONE(harness_avg=60.13%,see #3483)·next eval=350k(10k boundary=S2切换点)·report 43506B/66ckpt·10k cadence✅·
> **S2切换10-point ALL VERIFIED reconfirmed**:①shim 4226B✅(ls)②train.sh L202/206 BLEND_CURSOR_OFFSETS_JSON透传✅(grep)③pretrain_launcher.py L306 shim import✅(grep)④cursor_offsets_350k.json 1093B✅⑤blend_s2_preblend.tsv 3625B✅⑥s2_blend_switch_config.json✅⑦bridge 10/10✅⑧standalone 8/8✅⑨integration 7/7✅⑩S2_SWITCH_RUNBOOK.md 9节✅·
> **350k ETA**:iter=341240,remaining=8760 steps×7.27s≈63685s≈17.7h→~04:49 on 11-28·350k=eval+切换巧合:先切换(冷切换~10min)后eval(CPU-only ~76min,与S2训练并行)·
> **未碰训练/configs/.bak/daemon**(维护态铁律悍守)·evidence:worker_log tail-20(iter341240@11:07)·nvidia-smi 8×95-100%·ps daemon idle·train.sh grep L202/206✅·shim ls 4226B✅·pretrain_launcher.py grep L306✅·MEMORY≈15KB<32KB✅）
> #3483（2026-11-27 10:4x, 监控巡检·**340k eval DONE harness_avg=60.13%**·daemon idle waiting 350k·训练健康iter=341090/700000(48.73%) step avg10=7264ms=7.26s(✅below gate,eval-recovered)·S2切换全READY复验(10-point✅+SWITCH_RUNBOOK 9节✅)·350k ETA~04:30 on 11-28·
> 训练健康iter=341090/700000(48.73%) loss≈1.985-2.004(lr=1e-3,grad norm 0.086-0.130✅,0NaN/0skip✅)·step avg10=7264ms=7.26s(✅BELOW 7.4s gate)·latest10:7134/7134/7201/7229/7055/7287/7389/7583/7482/7152ms·spikes@341070(7583)/341080(7482)eval-caused,recovered@341090(7152)✅·GPU .29 8×96-100%/74501-74959MiB/74.5GB✅·load .29=29.45/29.35/29.25(224cores,eval just finished)·load .12=24.72/25.80/25.92·
> **340k eval DONE**:harness_avg=60.13%(arc_c38/arc_e64/boolq63/hella55/obqa39/piqa80/sciq85/wino57)·76.4min(09:31:33→10:47:58)·results.json 25967B·report regenerated 43962B/66ckpt·daemon idle sleeping 300s waiting 350k·10k filter verified L96-99✅·
> **S2切换ALL READY(10-point✅ reconfirmed)**:①shim 4226B✅②train.sh L203-207透传✅③pretrain_launcher.py L303-306✅④cursor_offsets_350k.json 1093B✅⑤blend_s2_preblend.tsv 3625B✅⑥s2_blend_switch_config.json✅⑦bridge 10/10✅⑧standalone 8/8✅⑨integration 7/7✅⑩SWITCH_RUNBOOK.md 9节✅(at run/data/blendswitch/)·
> **350k ETA**:iter=341090,remaining=8910 steps×7.26s≈17.9h→~04:30 on 11-28·350k=eval+切换巧合:先切换(冷切换~10min)后eval(CPU-only ~76min,与S2训练并行)·
> **未碰训练/configs/.bak/daemon**(维护态铁律悍守)·evidence:worker_log tail-30·nvidia-smi 8×96-100%·ps daemon idle·daemon log tail 340k DONE·results.json 25967B·report 43962B 66ckpt·10k filter L96-99✅·shim ls 4226B✅·SWITCH_RUNBOOK ls✅·MEMORY≈30KB<32KB✅）
> 📦 §#3474–#3482（2026-11-27 08:39–10:3x, 监控巡检+S2切换准备+340k eval·含#3479 train.sh BLEND_CURSOR_OFFSETS_JSON透传修复(BLOCKER,原#3477声称已修但未落盘→#3479重新修复)+#3477 Bridge Edition确认+S2_SWITCH_RUNBOOK.md创建+#3483 340k eval DONE harness=60.13%·训练健康step~7.1-7.5s·S2切换10-point ALL VERIFIED·eval未拖训练✅）→ daily-memories/2026-11-27.md；需要时再读。

> 📦 #3473（2026-11-27 08:22, 监控巡检·iter=339890 step avg10=7.90s 4 spikes>8s WORSENING·训练健康·340k NOT on disk ETA~08:36）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3472（2026-11-27 08:10, 监控巡检·iter=339810 step avg10=7.58s 2 spikes>8s·训练健康·340k NOT on disk）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3471（2026-11-27 07:56, 监控巡检·iter=339700 step avg10=7.31s<gate✅ 4th consecutive below·训练健康）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3470（2026-11-27 07:38, 监控巡检·iter=339550 step avg10=7.30s<gate✅ 3rd consecutive·训练健康）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3469（2026-11-27 07:25, 监控巡检·iter=339400 step avg10=7.26s<gate✅ 2nd consecutive·训练健康）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3468（2026-11-27 07:13, 监控巡检·iter=339350 step avg10=7.33s<gate✅ 1st below·训练健康）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3467（2026-11-27 06:52, 监控巡检·iter=339170 step avg10=7.57s>gate·训练健康·daemon idle）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3466（2026-11-27 06:42, 监控巡检·iter=339090 step avg10=7.60s>gate·训练健康·daemon idle）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3465（2026-11-27 06:35, 监控巡检·step avg10=7.59s>gate·训练健康iter=339030·daemon idle·autoqueue 57/57·eval_next=340k·纯监控）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3465（2026-11-27 06:35, 监控巡检·step avg10=7.59s>gate·训练健康iter=339030·daemon idle·autoqueue 57/57·eval_next=340k·纯监控）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 §#3462–#3464（2026-11-27 06:05–06:24, 监控巡检3轮·step avg10 8.08→7.72s持续改善·spikes 4→2→0·worst 9030→8497→7873ms·训练健康iter 338800→338940·daemon idle·autoqueue 57/57·eval_next=340k·纯监控）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3461（2026-11-27 05:58, 监控巡检·step avg10=8.04s>gate·训练健康iter=338760·daemon idle·autoqueue 57/57·eval_next=340k·纯监控）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 §#3457–#3460（2026-11-27 05:19–05:52, 监控巡检4轮·step avg10 7.64-8.08s(>7.4s gate,FLUCTUATING)·spikes 1-6·训练健康iter=338460-338710·daemon idle=NOT eval-caused·autoqueue 57/57·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 §#3447–#3456（2026-11-27 03:43–05:14, 监控巡检10轮·step avg10 oscillating 7.47-7.97s(>7.4s gate,WORSENING→IMPROVING cycles)·daemon idle=NOT eval-caused·训练健康iter=337710-338410·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3446（2026-11-27 03:43, 监控巡检·step avg10=7.47s(>7.4s gate)·训练健康iter=337710·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。

> 📦 #3445（2026-11-27 03:32, 监控巡检·step avg10=7.51s(>7.4s gate)·训练健康iter=337620·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。

> 📦 #3444（2026-11-27 03:18, 监控巡检·step avg10=7.78s(>7.4s gate,WORSENING)·训练健康iter=337500·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。

> 📦 #3443（2026-11-27 03:02, 监控巡检·step avg10=7.57s(>7.4s gate)·训练健康iter=337380·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。

> 📦 #3442（2026-11-27 02:53, 监控巡检·step avg10=7.61s(>7.4s gate,WORSENING)·训练健康iter=337310·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3440-#3441（2026-11-27 02:34-02:43, 监控巡检2轮·step avg10=7.49→7.52s(>7.4s gate,SLIGHTLY WORSENING)·daemon idle·训练健康iter=337170-337230·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 §#3431–#3439（2026-11-27 00:55–02:27, 监控巡检9轮·step avg10=7.49-7.78s(>7.4s gate,oscillating WORSENING)·daemon idle·训练健康iter=336360-337100·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3430（2026-11-27 00:29, 330k eval DONE✅ harness_avg=57.50%·step-time三段:pre-eval>7.4s(80min w/o eval)→during-eval peaked 7.97s→post-eval recovering 7.19s·训练iter=336170·daemon idle·autoqueue 57/57ckpt·eval_next=340k）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 §#3412–#3429（2026-11-26 18:41 – 2026-11-27 00:14, 放行autoqueue令+10k cadence变更·监控巡检~18轮·328k eval DONE(58.38%)→330k eval FAILED(killed step>7.4s)→10k cadence implemented(#3418)→330k eval RUNNING(76min)→DONE(57.50%)·step plateau 7.35-7.70s 80min w/o eval(pre-existing)→eval dragging→post-eval recovering·训练健康iter 333420→336060 step~7.0-8.0s·eval未拖训练✅·report 42783B→43506B(56→57ckpt)）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3417（2026-11-26 20:01, ⚠️EVAL KILLED—step persistently >7.4s·330k eval killed@~19:58·step avg10 trend 7.39s→8.0s+·per 11-21令 executed·daemon paused·训练健康iter=334050）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 §#3414–#3416（2026-11-26 19:11–19:32, 放行autoqueue令·330k eval RUNNING监控3轮·step avg10从7.39s→7.43s→7.47s(borderline 7.4s gate,eval adds ~0.04-0.08s)·训练健康iter 333660→333830·GPU 8×91-100%✅·autoqueue 56/56ckpt+330k RUNNING→后因step持续>7.4s于#3417 kill eval）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 #3413（2026-11-26 19:01, 监控巡检·daemon paused@19:00:37(step=7.41s>7.4s gate)·step borderline avg10=7.41s·训练健康iter=333570·autoqueue 56/56ckpt）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 #3412（2026-11-26 18:41, 监控巡检·328k eval DONE✅ harness_avg=58.38%·daemon paused@18:40:36(step=7.42s)·训练健康iter=333420·autoqueue 56/56ckpt）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 §#3407–#3411（2026-11-26 17:19–18:23, 监控巡检5轮·328k eval RUNNING监控(17:24 start,daemon 2×pause step>7.4s→resume→eval 76min)·step elevated avg10=7.38-7.61s(>7.4s gate borderline,daemon auto-pause/resume)·训练健康step~7.2-7.7s·328k于18:40 DONE=58.38%见#3412·eval未拖训练✅）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 §#3390–#3406（2026-11-25 19:43 – 2026-11-26 17:11, 监控巡检~17轮·326k eval DONE(58.88%)→328k eval RUNNING/PAUSED/kill/retry·sympy FIX(#3396,daemon stuck 40h→restored)·step spike→kill→recover·backlog全清·eval未拖训练✅·report多次regen）→ daily-memories/2026-11-26.md；需要时再读。

> 📦 #3379-#3380（2026-11-25 16:40-17:08, 监控巡检·320k eval DONE harness_avg=54.62%·⚠️step time spike(320680-320750,7.64-8.14s,harness CPU争抢NOT eval-caused)→17:08已恢复avg=7.22s·报告修复regen→40882B(52/52ckpt)）→ daily-memories/2026-11-25.md；需要时再读。


> 📦 #3381-#3382（2026-11-25 17:21-17:37, 监控巡检2轮·daemon idle无eval负载·训练健康iter321030-321160 step7.21-7.40s(all≤7.4s✅,1单点spike NOT sustained)·GPU 8×81-100%✅·load正常·报告=40882B(52/52ckpt)✅·research日报11-25已noted(长上下文温度校准/loop residual/TinyLlama对照/Llemma三源配比/phi-1.5 synthetic消融),无即时action）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3383-#3384（2026-11-25 18:05-18:12, 监控巡检2轮·daemon idle无eval负载·训练健康iter321400-321450 step7.19-7.22s(all<7.4s✅)·报告修复regen·GPU正常·load正常）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3385（2026-11-25 18:26, 监控巡检·daemon idle·autoqueue令持续履行·训练健康iter321580 step7.22s·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3386（2026-11-25 18:35, 监控巡检·daemon idle·autoqueue令持续履行(52/52ckpt)·322k NOT on disk·训练iter=321640 step7.29s·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3387（2026-11-25 18:52, 监控巡检·daemon idle·autoqueue令持续履行(52/52ckpt)·322k NOT on disk·训练iter=321790 step7.28s·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3388（2026-11-25 19:03, 监控巡检·daemon idle·autoqueue 52/52ckpt(10k-320k)✅·322k NOT on disk·训练iter=321880 step7.21s·报告40882B·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3376-#3378（2026-11-25 16:02-16:32, 监控巡检3轮·320k eval RUNNING→DONE·step正常(7.20-7.26s,0>7.4s✅)·eval未拖训练✅·报告修复(regen→40400B 51/51ckpt)）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3375（2026-11-25 15:45, 监控巡检·320k eval RUNNING·step7.25s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3374（2026-11-25 15:33, 监控巡检+报告修复·320k eval RUNNING·报告修复(vision auto-commit revert→regen 51/51ckpt 40400B✅)·step7.24s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3373（2026-11-25 15:20, 监控巡检·320k eval RUNNING·step7.22s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。


> 📦 §#3340–#3372（2026-11-25 08:43–15:10, 放行autoqueue令·监控巡检~30轮·312k/314k/316k/318k eval DONE(harness:312k=55.62%/314k=56.25%/316k=57.38%/318k=56.25%)·daemon print口径修复(#3365 acc_only→harness_avg)·⚠️daemon stuck 9h(312k:01_convert_hf_to_gguf.sh git untrack→recovered 08:32)·训练健康step~7.15-7.50s·backlog 270k-318k全清51/51ckpt·eval未拖训练✅·report多次修复regen(vision auto-commit覆盖→恢复)）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 §#3208–#3338（2026-11-24 00:12–19:15, 放行autoqueue令·监控巡检~40轮·300k/302k/304k/306k/308k/310k eval DONE(300k=56.88%/302k=59.13%/304k=59.00%/306k=59.25%/308k=58.38%)·训练健康step~7.0-7.5s·backlog 270k-310k全清46/46ckpt·270k=59.75%/272k=56.75%积压点已补评✅·eval未拖训练✅·L1报告多次regen·step-time spike(320680-320750,7.64-8.14s,harness CPU争抢NOT eval-caused)）→ daily-memories/2026-11-24.md；需要时再读。

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
 