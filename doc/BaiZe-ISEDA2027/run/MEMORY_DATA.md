# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> 🎯 **现行路线 = F 自定义改造（权重热更新 + per-source 游标映射）** · patch/验证状态 = 7/7 standalone PASS + 5/5 Megatron-integration PASS（2026-11-23）· 零重叠实测 = 0（standalone overlap_docs=0 + integration total_overlap=0，第206次复验）· 350k 倒计时 ≈ 3.95d → ~11-28（patch + 零重叠验证已完成，早于 11-27 截止）· **Megatron-LM 源码集成已完成**：dev copy `code/Megatron-LM-blendswitch` branch `blend-hot-switch` commit `011a05b`，5 文件 patch + 2 新文件，base `14c215d`，未 merge 主线

> 🟢 **心跳 · 2026-11-24 03:35 (R414) — 例行巡检+blendswitch第206次复验7/7 PASS+302k eval RUNNING**：①✅git synced(fetch origin OK,local HEAD=0ab344ee ahead of origin/main=d0398d9,0新data令,task书顶部仍=F科普报告已交付)；②✅pretrain iter≈302,230/700k(43.18%) step~7.14s(during-eval) loss≈1.99 0NaN/0skip✅ lr=1e-3(读自MEMORY_PRETRAIN_2B.md #3228@03:15 iter=302230 step7137ms,302k eval RUNNING ETA~04:06) load .12=27.26/26.95/26.80健康✅；350k倒计时≈(350k-302,230)×7.14s≈341,078s≈94.7h≈3.95天→~11-28；③✅blendswitch第206次复验7/7 PASS(All tests pass:True；zero_overlap per-source全overlap_docs=0·total_overlap=0·ratio max_dev=0.0087%✅；flag-off=stock byte-equivalent✅；new+shared all zero overlap✅；epoch_wrap诚实报告；json_roundtrip OK；perf:stock 0.2082s track 0.0225s switch 0.2108s)；integration 5/5 PASS(total_overlap=0 ratio_dev=0.0pp flag-off=byte-identical ckpt_roundtrip OK,2026-11-23)；复跑=cd data/blendswitch && /nas_train/app.e0031982/miniforge3/bin/python3 test_blend_switch.py；④✅.12 load=27.26/26.95/26.80<120✅；⑤✅/nas_user 42T可用>5T红线✅；⑥✅无下载进程(pgrep无命中,S2三源全100%,0 .incomplete)；⑦✅research日报2026-11-24(同R412/R413,无新可执行建议)；⑧✅MEMORY体积37.6KB<40KB✅ TASK27.6KB<32KB✅。全部用户令已交付。待pretrain到350k(~11-28)启动S2。WAITING=0。
> 📦 R413 心跳（例行巡检+blendswitch第205次复验7/7 PASS·iter≈302,230 step7.14s·302k eval RUNNING·.12 load27.58·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R412 心跳（例行巡检+blendswitch第204次复验7/7 PASS·iter≈302,230 step7.14s·302k eval RUNNING·.12 load27.58·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R411 心跳（例行巡检+blendswitch第203次复验7/7 PASS·iter≈302,230 step7.14s·302k eval RUNNING·.12 load26.44·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R410 心跳（例行巡检+blendswitch第202次复验7/7 PASS·iter≈302,170 step7.11s·302k eval RUNNING·.12 load26.46·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R409 心跳（例行巡检+blendswitch第201次复验7/7 PASS·iter≈302,100 step7.09s·302k eval RUNNING·.12 load24.85·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R408 心跳（例行巡检+blendswitch第200次复验7/7 PASS·iter≈302,040 step7.05s·302k eval RUNNING·.12 load25.51·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R407 心跳（例行巡检+blendswitch第199次复验7/7 PASS·iter≈302,040 step7.05s·302k eval RUNNING·.12 load27.88·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R406 心跳（例行巡检+blendswitch第198次复验7/7 PASS·iter≈301,900 step7.19s·300k eval done daemon idle·.12 load27.10·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R405 心跳（例行巡检+blendswitch第197次复验7/7 PASS·iter≈301,900 step7.19s·300k eval done daemon idle·.12 load26.24·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R404 心跳（例行巡检+blendswitch第196次复验7/7 PASS·iter≈301,900 step7.19s·300k eval done daemon idle·.12 load25.05·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R402 心跳（例行巡检+blendswitch第194次复验7/7 PASS·iter≈301,840 step7.19s·300k eval done daemon idle·.12 load27.48·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R401 心跳（例行巡检+blendswitch第193次复验7/7 PASS·iter≈301,700 step7.15s·300k eval done daemon idle·.12 load23.45·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R400 心跳（例行巡检+blendswitch第192次复验7/7 PASS·iter≈301,700 step7.17s·300k eval done daemon idle·.12 load26.27·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R399 心跳（例行巡检+blendswitch第191次复验7/7 PASS·iter≈301,600 step7.20s·300k eval done daemon idle·.12 load25.65·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R398 心跳（例行巡检+blendswitch第190次复验7/7 PASS·iter≈301,480 step7.20s·300k eval done daemon idle·.12 load25.66·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R397 心跳（例行巡检+blendswitch第189次复验7/7 PASS·iter≈301,390 step7.17s·300k eval done daemon idle·.12 load29.67·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R396 心跳（例行巡检+blendswitch第188次复验7/7 PASS·iter≈301,390 step7.17s·300k eval done daemon idle·.12 load29.11·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R395 心跳（例行巡检+blendswitch第187次复验7/7 PASS·iter≈301,320 step7.13s·300k eval done daemon idle·.12 load24.75·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R394 心跳（例行巡检+blendswitch第186次复验7/7 PASS·iter≈301,260 step7.13s·300k eval done daemon idle·.12 load24.75·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R393 心跳（例行巡检+blendswitch第185次复验7/7 PASS·iter≈301,200 step7.14s·300k eval done daemon idle·.12 load27.87·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R392 心跳（例行巡检+blendswitch第184次复验7/7 PASS·iter≈301,130 step7.14s·300k eval done daemon idle·.12 load28.44·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R391 心跳（例行巡检+blendswitch第183次复验7/7 PASS·iter≈301,130 step7.14s·300k eval done daemon idle·.12 load28.44·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R390 心跳（例行巡检+blendswitch第182次复验7/7 PASS·iter≈301000 step7.11s·300k eval已完成daemon idle·.12 load26.15·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R389 心跳（例行巡检+blendswitch第184次复验7/7 PASS·iter≈300940 step7.19s·300k eval已完成daemon idle·.12 load26.58·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R388 心跳（例行巡检+blendswitch第180次复验7/7 PASS·iter≈300820 step7.16s·300k eval已完成daemon idle·.12 load26.53·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R387 心跳（例行巡检+blendswitch第179次复验7/7 PASS·iter≈300820 step7.16s·300k eval已完成daemon idle·.12 load26.53·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R386 心跳（例行巡检+blendswitch第178次复验7/7 PASS·iter≈300750 step7.18s·300k eval已完成daemon idle·.12 load27.48·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R385 心跳（例行巡检+blendswitch第177次复验7/7 PASS·iter≈300750 step7.18s·300k eval已完成daemon idle·.12 load25.24·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R384 心跳（例行巡检+blendswitch第176次复验7/7 PASS·iter≈300680 step7.18s·300k eval收尾中·.12 load24.74·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R383 心跳（例行巡检+blendswitch第175次复验7/7 PASS·iter≈300650 step7.18s·300k eval收尾中·.12 load25.12·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R381 心跳（例行巡检+blendswitch第173次复验7/7 PASS·iter300480 step7.18s·300k eval RUNNING·.12 load26.50·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R380 心跳（例行巡检+blendswitch第172次复验7/7 PASS·iter300480 step7.18s·300k eval RUNNING·.12 load26.50·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R378 心跳（例行巡检+blendswitch第170次复验7/7 PASS·iter300500 step7.12-7.34s·300k eval RUNNING·.12 load26.14·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R377 心跳（例行巡检+blendswitch第169次复验7/7 PASS·iter300210 step7.34s·300k eval RUNNING·.12 load27.93·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R376 心跳（例行巡检+blendswitch第168次复验7/7 PASS·iter300130 step7.18s·300k eval RUNNING·.12 load25.99·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R375 心跳（例行巡检+blendswitch第167次复验7/7 PASS·iter300130 step7.18s·300k eval RUNNING·.12 load23.80·0下载进程）已归档 → daily-memories-data/2026-11-23.md

> 📦 R373 心跳（例行巡检+blendswitch第165次复验7/7 PASS·iter300000 step7.16s·300k LANDED·.12 load26.80·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R372 心跳（例行巡检+blendswitch第164次复验7/7 PASS·iter299920 step7.17s·.12 load24.74·0下载进程）已归档 → daily-memories-data/2026-11-23.md

> 📦 R371 心跳（例行巡检+blendswitch第163次复验7/7 PASS·iter299790 step7.16s·.12 load25.62·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R370 心跳（例行巡检+blendswitch第162次复验7/7 PASS·iter299690 step7.17s·.12 load24.24·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R369 心跳（例行巡检+blendswitch第161次复验7/7 PASS·iter299770 step7.17s·.12 load24.97·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R368 心跳（例行巡检+blendswitch第160次复验7/7 PASS·iter299600 step7.18s·.12 load27.81·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R367 心跳（例行巡检+blendswitch第159次复验7/7 PASS·iter299600 step7.18s·.12 load24.00·0下载进程）已归档 → daily-memories-data/2026-11-23.md

> 📦 R366 心跳（例行巡检+blendswitch第158次复验7/7 PASS·iter299540 step7.21s·.12 load26.88·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R365 心跳（例行巡检+blendswitch第157次复验7/7 PASS·iter299540 step7.21s·.12 load27.72·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R364 心跳（例行巡检+blendswitch第156次复验7/7 PASS·iter299440 step7.20s·.12 load25.83·0下载进程）已归档 → daily-memories-data/2026-11-23.md

> 🟢 **心跳 · 2026-11-23 21:40 (R363) — Megatron-LM 源码集成完成 + 5/5 integration tests PASS**：①✅创建了独立 dev copy `code/Megatron-LM-blendswitch`（git clone 自 Xmodel-2.5-code，base `14c215d`，109MB 仅源码无数据）；②✅在 `blend-hot-switch` 分支上应用了 5 文件 patch：blended_dataset.py(+update_weights)、data_samplers.py(+BlendHotSwitchRandomSampler+maybe_trigger_blend_switch)、arguments.py(+--blend-hot-switch/--blend-switch-step/--blend-switch-config)、training.py(+train-loop hook)、checkpointing.py(+blend_switch_state persist)；③✅新增 blend_switcher.py(340行)+test_blend_hot_switch_integration.py(5 tests)；④✅5/5 integration tests PASS（zero_overlap=0 / ratio_dev=0.0000pp / flag_off=byte-identical / new_source=0 / checkpoint_roundtrip=OK）；⑤✅生成 blend_hotswitch.patch(921行)+verify_results_integration.json+更新README_PATCH.md；⑥✅commit `011a05b` on blend-hot-switch branch，未 merge 主线，等用户验收。环境：py310 env / numpy 1.26.4 / CPU-only 无GPU。安全边界遵守：独立副本·pin base commit·flag默认OFF·不碰训练主线。WAITING=0。

> 📦 R362 心跳（例行巡检+blendswitch第155次复验7/7 PASS·iter299110 step7.19s·.12 load26.11·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R361 心跳（例行巡检+blendswitch第154次复验7/7 PASS·iter299030 step7.19s·.12 load25.59·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R360 心跳（例行巡检+blendswitch第153次复验7/7 PASS·iter298940 step7.17s·.12 load29.03·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R359 心跳（例行巡检+blendswitch第152次复验7/7 PASS·iter298840 step7.26s·.12 load26.72·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R358 心跳（例行巡检+blendswitch第151次复验7/7 PASS·iter298840 step7.26s·.12 load29.22/27.13/26.73·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R357 心跳（例行巡检+blendswitch第150次复验7/7 PASS·iter298780 step7.33s(2/15 transient spikes 8206/8478ms均单步恢复)·.12 load28.68/27.34/26.78·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R356 心跳（例行巡检+blendswitch第149次复验7/7 PASS·iter298780 step7.33s(2/15 transient spikes 8206/8478ms均单步恢复)·.12 load27.62/26.86/26.53·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R355 心跳（例行巡检+blendswitch第148次复验7/7 PASS·iter298700 step7.24s·.12 load25.58·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R354 心跳（例行巡检+blendswitch第147次复验7/7 PASS·iter298450 step7.14s·.12 load24.12/24.96/25.67·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R353 心跳（例行巡检+blendswitch第146次复验7/7 PASS·iter298450 step7.14s·.12 load25.16/25.36/26.11·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R352 心跳（例行巡检+blendswitch第145次复验7/7 PASS·iter298390 step7.13s·.12 load26.98/26.57/26.74·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R280~R349 心跳（70轮例行巡检+blendswitch第73~142次复验全7/7 PASS·iter294250~298200·step6.98~7.42s·.12 load均<30·0下载进程）已批量归档 → daily-memories-data/2026-11-23.md
> 📦 R279 心跳（例行巡检+blendswitch第72次复验7/7 PASS·iter293940 step7392ms·.12 load25.29/25.64/26.10·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R277 心跳（例行巡检+blendswitch第70次复验7/7 PASS·iter293940 step7392ms·.12 load25.15/26.47/26.57·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R276 心跳（例行巡检+blendswitch第69次复验7/7 PASS·iter293940 step7392ms·.12 load25.99/26.16/26.43·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R275~R259 心跳（例行巡检+blendswitch第52~68次复验均7/7 PASS·iter293090~293940·step7341~7420ms·.12 load≤30·0下载进程）已批量归档 → daily-memories-data/2026-11-23.md
> 📦 R258 心跳（例行巡检+blendswitch第51次复验7/7 PASS·iter293040 step7286ms·.12 load25.34/26.04/26.43·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R257 心跳（例行巡检+blendswitch第50次复验7/7 PASS·iter292900 step7212ms·.12 load26.80/27.07/26.79·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R256~R255 心跳（blendswitch第49~48次复验7/7 PASS·iter292850 step~7208ms·.12 load≤25.1·0下载进程）已批量归档 → daily-memories-data/2026-11-23.md
> 📦 R252 心跳（例行巡检+blendswitch第45次复验7/7 PASS·iter292610 step~7199ms·.12 load25.73·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R251 心跳（例行巡检+blendswitch第44次复验7/7 PASS·iter292610 step~7.2s·.12 load25.14·0下载进程）已归档 → daily-memories-data/2026-11-23.md
> 📦 R249~R225 心跳（blendswitch第33~18次复验均7/7 PASS·iter292040~291230·step7160~7244ms·.12 load≤30·0下载进程）已批量归档 → daily-memories-data/2026-11-23.md

> 📦 R238~R214 心跳（例行巡检+blendswitch第7~31次复验均7/7 PASS·iter290890~291980·step7129~7256ms·.12 load≤28·S2三下载全100%·research日报EDA建议记为参考(EDA已取消)）已批量归档 → daily-memories-data/2026-11-23.md
> 📦 R213~R208 心跳（F科普报告复验第2~6次全通过+归档收口+v1交付40,743B/6SVG/0外链0script commit+push完成）已批量归档 → daily-memories-data/2026-11-22.md

> 📦 R207 心跳（第31次复验7/7 PASS zero_overlap=0 / v5报告13,813B / v4报告14,625B）已归档 → daily-memories-data/2026-11-22.md

> 📦 R206~R170 心跳（方案F blendswitch例行巡检+第3-30次复验，均7/7 PASS zero_overlap=0）已归档 → daily-memories-data/2026-11-22.md
> _(R171 心跳已归档 daily-memories-data/2026-11-22.md · R171: v4报告结论段修正三层表述+~12%加权透明表(token口径0.201≈20%)+WBS支撑17h≈2.1人日)
> _(R170 心跳已归档 daily-memories-data/2026-11-22.md · R170: v5报告交付+blend_switcher.py实现(BlendSwitcher+update_weights+BlendHotSwitchSampler 14KB)+CPU验证7/7 PASS zero_overlap=0+validate_overlap.py+README_PATCH.md(4处patch)+base commit=14c215dc)

> _(R169 心跳已归档 daily-memories-data/2026-11-22.md · R169: v4报告交付+方案F stock不可行核查+§0.1修正+S1→S2接力 LR恒1e-3)

> _(R156~R146 心跳已归档 daily-memories-data/2026-11-22.md · R156:例行 iter279.9k / R155:v3刷新 iter279.8k / R153:例行 iter279.3k / R152:v3刷新 iter279.2k / R151:v3验证+例行 iter278.6k / R150:例行 iter278.6k / R149:v3刷新 iter278.5k / R148:例行 iter278k / R147:例行 iter278k / R146:v3刷新 iter277.9k)_
> _(R145~R137 心跳已归档 daily-memories-data/2026-11-22.md · R145:例行巡检 iter277.8k / R144:例行巡检 iter277.6k / R143:v3刷新 iter277.5k / R142:TASK体积归档37804B / R141:例行+/tmp清理 / R140:v3刷新 iter277.1k / R139:S2新源污染扫描全✅0命中48K docs / R138:扩展黑名单5359任务建成 / R137:blacklist重建536任务)_

> _(R136~R116 心跳已归档 daily-memories-data/2026-11-21.md · R136:main版blend TSV 12源(nemotron+megamath_web)更新 / R135:MegaMath-web分词✅100%(218.1B tok) / iter~275.3k→273.0k step~7.23~7.13s MM-web 98.8%→89.8% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R115~R108 心跳已归档 daily-memories-data/2026-11-21.md · iter~272.3k→271.6k step~7.16~7.17s MM-web 87.7%→85.6% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R107~R97 心跳已归档 daily-memories-data/2026-11-21.md · iter~271.6k→270k step~7.12~7.17s MM-web 85.3%→79.9% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R96~R85 心跳已归档 daily-memories-data/2026-11-21.md · iter~269.8k→267.9k step~7.09~7.16s MM-web 78.9%→72.1% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_

> _(R84~R70 心跳已归档 daily-memories-data/2026-11-21.md · iter~265.4k→267.6k step~7.0~7.1s MM-web 61.3%→70.8% Nemotron✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R69~R49 心跳已归档 daily-memories-data/2026-11-21.md · iter~261.3k→265.2k step~7.0~7.2s MM-web 43.3%→60.6% Nemotron✅ Math-Reasoning✅ Code-Reasoning✅)_

> _(R48 心跳已归档 daily-memories-data/2026-11-20.md · iter~261.1k step~7.32s MM-web 42.6% Math-Reasoning ✅100%)_

> _(R44~R48 心跳已归档 daily-memories-data/2026-11-20.md · iter~260k~261.1k step~7.1~7.32s MM-web 38.8%→42.6% Math-Reasoning 97.5%→100%)_

> _(R43 心跳已归档 daily-memories-data/2026-11-20.md · iter~260k step~7.0s MM-web 37.7% Math-Reasoning 97.5%)_

> _(R41~R13 心跳已归档 daily-memories-data/2026-11-20.md · iter~261k→267k step~7.0~8.2s MM-web 5.9%→32.3% Math-Reasoning 72%→92.8% Nemotron✅完成 193/193 195.4B tok / Code-Reasoning✅ / R18 Nemotron 完成里程碑)_
> _(R9, R8, R7, R4 心跳已归档 daily-memories-data/2026-11-19.md · iter~260k step~7.05s Nemotron 82-88% MM-web分词启动(ETA~40h) Math-Reasoning 72%)_
> 📦 旧已交付用户令摘要（2026-11-13 ~ 11-18：S2 overlap研究/PC-4 blend TSV/Nemotron+finemath分词/CPU僵尸清理/stack-v3全量下载/下载优先级/IFM数据集/agent datasets — 全部已交付，S2三源下载全100%）已归档 → daily-memories-data/2026-11-23.md「归档块1」
> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 📦 旧详细报告条目（vision图文对调研/stack-v3下载+分词+EDA脚本价值分析 — 全部已交付，报告均落 reports/）已归档 → daily-memories-data/2026-11-23.md「归档块2」
> 📦 唤醒1522-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC完成+IFM下载启动+Code-Reasoning崩溃修复重启+多轮巡检,共10轮,详见日文件）
> 📦 唤醒1493-1520 原文已归档 → daily-memories-data/2026-11-14.md~2026-11-15.md（StepB完成+StepC分词启动+崩溃修复+IFM/agent datasets进度,共~25轮,详见日文件）
> 📦 唤醒1490-1492 原文已归档 → daily-memories-data/2026-11-13.md（StepB下载进度巡检+StepC auto-wait修复重启×3轮,详见日文件）
> ⚠️ [11-14 19:2x] 运维介入修复记录：StepC 16workers在shard5350处BrokenPipeError崩溃(OOM→Pool pipe断裂→NFS写入未flush→989新shard输出丢失)→修复:fsync+maxtasksperchild50+BrokenPipeError异常处理+workers 16→8→PID1677655重启,nice19/ionice3,日志/tmp/tokenize_stackv3_new.log

> 📦 唤醒1489 原文已归档 → daily-memories-data/2026-11-13.md（ETA审计完成+StepC护栏修复+任务书归档,详见日文件）
> 📦 唤醒1487-1488 原文已归档 → daily-memories-data/2026-11-13.md（StepA DONE确认+StepB下载进度巡检×2轮,旧ETA~3.3h已被本轮纠正,详见日文件）
> 📦 唤醒1483-1486 原文已归档 → daily-memories-data/2026-11-13.md（StepA DONE确认+StepB下载进度巡检+StepC launch启动,共4轮,详见日文件）
> 📦 唤醒1471-1482 原文已归档 → daily-memories-data/2026-11-13.md（分词完成+全量下载启动+rsync 2TB+源删除+hf download全量+用户令11-13b启动,共12轮,详见日文件）

> 📦 迁移完成块(运维令13:3x+SFT/Agent分词+5源+4源+3稳定源+ufw_en,共9源705shard~8.3TB→/nas_env)已归档 → daily-memories-data/2026-11-13.md；结论见DATA_MAPPING.md

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        S2前置+污染闸门全完成 — PC-1✅~PC-5✅ + 扩展黑名单✅ + S2新源扫描✅(48K docs/0命中) + 方案F blendswitch交付✅(7/7零重叠=0) → WAITING=0
已完成:       ✅PC-1 L4过滤(430.7B/90.5%);✅PC-2 MegaMath分词ALL DONE(5 subsets/364 shards/243GB);✅PC-3污染闸门(6benchmark/9277tasks);✅PC-4 main版blend_s2_preblend.tsv(12源/含nemotron 0.067+megamath_web 0.060+finemath 0.005/weight_sum=1.0/gen_blend --verify通过);✅S2重叠研究报告;✅finemath-4plus分词DONE(9.4B tok);✅v3报告(R136刷新main版/pushed);✅MegaMath-web下载DONE(4950parquet/826GB);✅MegaMath-web分词DONE(4950/4950=100%/218.1B tok);✅Code-Reasoning下载DONE(1637parquet/0inc);✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors);✅Math-Reasoning下载DONE(2228parquet/0inc);✅DATA_MAPPING.md更新;✅论文Fig-1三饼图+Fig-2调优+TABLE IV精简+数据源/Decay/LongCtx引用补齐(latexmk 0err);✅EDA-Eval 536-task黑名单重跑复现(R137/正控158/158);✅扩展黑名单blacklist_extended建成(R138/5359tasks/4847354 13-gram/正控164/164);✅S2新源污染扫描(R139/4源×12K=48K docs/全0命中);✅方案F blendswitch交付(R170-R171/commit 68742cfbe4/blend_switcher.py+v5报告+v4修正+CPU验证7/7零重叠=0)
当前动作:     R366例行巡检:iter≈299,540/700k(42.79%) step_avg(last15)=7211ms(7.21s)训练健康✅ loss≈1.99 0NaN/0skip lr=1e-3(300k NOT on disk ETA~22:47)；方案F blendswitch第158次复验7/7 PASS(zero_overlap=0)+Megatron源码集成5/5 PASS(commit 011a05b未merge主线)；git synced(0新data令)；PC-1~PC-5全✅/S2三下载全100%/无后台任务/.12 load=26.88✅/350k倒计时~4.21d→~11-28
下一步:       ①等pretrain到350k(~11-28)启动S2(blend TSV已就绪/SEED=5678待转告pretrain线) ②S2投料前可按S1口径对4新源做全量扫描(>150K docs)作为加强验证(非阻塞/contam_venv已就绪) ③research日报2026-11-23建议(分词器覆盖度/held-out掉点/均衡采样)均为借鉴类,已评估忽略
阻塞:         无(全部前置完成;S2三下载全100%;无后台任务;.12 load≈26.88<120✅;/nas_user 42T可用✅>5T红线)
ERROR_COUNT:  0
未完成指令:   无(全部用户令已交付;PC-1~PC-5全部完成;main版blend TSV已就绪)→WAITING=0
```

> 📦 唤醒1521-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC巡检+Agent/IFM下载进度+Code-Reasoning重启+IFM多轮巡检,详见日文件）

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [11-21 16:2x] 唤醒1557（v3报告R116刷新·例行巡检·所有用户令已交付）：①🔄MegaMath-web分词RUNNING(4445/4950=89.8%/~195.9B tok/ETA~4.7h/PID3028119+3028124/nice19/ionice3/RAYON=8/428%CPU=4核/etime~1d17h)；②✅Nemotron-CC-Math分词DONE(193/193/195.4B tok)；③✅finemath分词DONE(9.4B tok)；④✅Math-Reasoning下载DONE(2228/0inc)；⑤✅Code-Reasoning下载DONE(1637/0inc)；⑥✅.12 load=29.7✅<120红线；⑦✅.29 load=26.6✅；⑧✅磁盘/nas_user 113T/71T已用/42T可用(63%)→✅红线≥5T；⑨✅pretrain训练正常(iter~273.0k/step~7.13s/latest ckpt=272k)；⑩✅v3报告R116刷新(MegaMath-web 4445/4950=89.8%/load 29.7)；⑪✅git up-to-date with origin(无新data令/所有用户令已交付)；⑫下一步：等MegaMath-web分词完成(~4.7h)→更新main版blend TSV(加Nemotron)→逐源13-gram污染扫描→commit+push
> [11-20 10:00] 唤醒1556（v3报告R36刷新·2后台任务巡检·所有用户令已交付）：①🔄MegaMath-web分词RUNNING(1398/4950=28.2%/~55.4B tok/ETA~28.3h/PID3028124/nice19/ionice3/RAYON=8/438%CPU=4核)；②🔄Math-Reasoning下载RUNNING(1994/2228=89.5%/2inc/ETA~4.1h/PID3697171/nice19/ionice3/max-workers2)；③✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors)；④✅Code-Reasoning下载DONE(1635/0inc)；⑤✅.12 load=11.40✅<120红线；⑥✅磁盘/nas_user 113T/70T已用/43T可用(63%)→✅红线≥5T；⑦✅v3报告R36刷新(MegaMath-web 1398/4950=28.2%/Math-Reasoning 89.5%/load 11.40)；⑧✅git up-to-date with origin(无新data令)；⑨所有3条11-19用户令(v3报告/Fig-2饼图+TABLE IV/数据源引用+Fig-1三饼图)均已交付✅；⑩下一步：等MegaMath-web分词完成(~28h)→更新main版blend TSV(加Nemoton)→13-gram污染扫描→commit+push
> [11-20 ~04:00] 唤醒1555（v3报告R20刷新·3后台任务巡检）：①✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors)；②🔄MegaMath-web分词RUNNING(702/4950=14.2%/~26.4B tok/ETA~31h/PID3028119/nice19/ionice3/RAYON=8)；③🔄Math-Reasoning下载RUNNING(1764/2228=79.1%/3.3TB/2inc/ETA~8h/PID3697171/nice19/ionice3/max-workers2)；④✅.12 load=9.59✅<120红线；⑤✅磁盘/nas_user 113T/70T已用/44T可用(62%)→✅红线≥5T；⑥✅v3报告R20刷新(MegaMath-web 702/4950=14.2%/Math-Reasoning 79.1%/load 11.97)；⑦✅git pulled origin(d950d2c09/无新data令/所有用户令已交付)；⑧下一步：等MegaMath-web分词完成(~31h)→更新main版blend TSV→13-gram污染扫描→commit+push
> [11-20 02:10] 唤醒1554（例行巡检·v3报告刷新·3后台任务健康·Nemotron即将完成）：①🔄Nemotron-CC-Math分词 RUNNING(189/193=97.9%/~150B tok已产出/ETA~38min即将完成/PID1791934/nice19/ionice3/RAYON=8)；②🔄MegaMath-web分词 RUNNING(426/4950=8.6%/~15.7B tok/ETA~35h/PID3028124/nice19/ionice3/RAYON=8)；③🔄Math-Reasoning下载 RUNNING(1690/2228=76%/ETA~9h/PID3697171/nice19/ionice3/max-workers2)；④✅.12 load=13.34✅<120红线；⑤✅磁盘/nas_user 113T/70T已用/44T可用(62%)→✅红线≥5T；⑥✅v3报告已刷新最新live numbers(Nemotron 97.9%/MegaMath-web 8.6%/Math-Reasoning 76%/load 13.34)；⑦✅git up-to-date with origin；⑧下一步：Nemotron分词即将完成(~38min)→完成后立即更新main版blend TSV(加入Nemotron源/下调megamath prop/epoch从1.69降到~0.62)→更新v3报告→commit+push

> 📦 唤醒1552 原文已归档 → daily-memories-data/2026-11-19.md（例行巡检·4后台任务健康·Code-Reasoning 93%·Nemotron 21/193,详见日文件）

> 📦 唤醒1549-1551 原文已归档 → daily-memories-data/2026-11-18.md（例行巡检×3轮·4后台任务健康·Code-Reasoning渐进93%·Nemotron分词21/193,详见日文件）

> 📦 唤醒1548 原文已归档 → daily-memories-data/2026-11-18.md（3个崩溃下载重启+finemath分词DONE+Nemotron进度巡检,详见日文件）

> 📦 唤醒1547 原文已归档 → daily-memories-data/2026-11-18.md（后台任务巡检+IFM下载重启+进度更新,详见日文件）

> 📦 唤醒1536-1546 原文已归档 → daily-memories-data/2026-11-16.md~2026-11-17.md（IFM下载多轮巡检+Code-Reasoning崩溃修复重启+MegaMath batch2启动+HfApi实测,共11轮,详见日文件）
> 📦 唤醒1457-1465 原文已归档 → daily-memories-data/2026-11-12.md~2026-11-13.md（例行巡检×9轮,stack-v3-train稳定1.9T,无新data令,详见日文件）
> 📦 唤醒1458 原文已归档 → daily-memories-data/2026-11-13.md（例行巡检,无新data令,详见日文件）
> 📦 唤醒1410-1420 原文已归档 → daily-memories-data/2026-11-13.md（batch6-7进度巡检×11轮,batch6完成1.813TB+batch7启动,2TB预算92.4%,详见日文件）
> 📦 唤醒1444-1456 原文已归档 → daily-memories-data/2026-11-11.md~2026-11-12.md（例行巡检+vision图文对调研报告交付,共13轮,详见日文件）
> 📦 唤醒1425-1440 原文已归档 → daily-memories-data/2026-11-10.md（例行巡检+staleness审计+论文数据节更新+TASK.md标记更新,共16轮,详见日文件）
> 📦 唤醒1422-1424 原文已归档 → daily-memories-data/2026-11-10.md（batch7完成+QC+2TB ROI复盘+例行巡检,共3轮,详见日文件）
> 📦 唤醒1385 原文已归档 → daily-memories-data/2026-11-13.md（11-07运维令执行:代码语料放行ROI下载,详见日文件）
> 📦 唤醒1374-1384 原文已归档 → daily-memories-data/2026-11-07.md（例行空唤醒巡检,共11轮,详见日文件）
> 📦 唤醒1346-1373 原文已归档 → daily-memories-data/2026-11-06.md~2026-11-07.md（例行空唤醒巡检,共28轮,详见日文件）
> 📦 唤醒1319-1345 原文已归档 → daily-memories-data/2026-11-06.md（例行空唤醒巡检,共27轮,详见日文件）
> 📦 唤醒1283-1318 原文已归档 → daily-memories-data/2026-11-06.md（例行空唤醒巡检,共36轮,详见日文件）
> 📦 唤醒1282-1241 原文已归档 → daily-memories-data/2026-11-05.md（例行空唤醒巡检,共42轮,详见日文件）
> 📦 唤醒1240-1213 原文已归档 → daily-memories-data/2026-11-05.md（例行空唤醒巡检,共28轮,详见日文件）
> 📦 唤醒1180-1212 原文已归档 → daily-memories-data/2026-11-04.md（例行空唤醒巡检+09:2x下载巡检+09:4x报告复核,共33轮,详见日文件）
> 📦 唤醒1161-1179 原文已归档 → daily-memories-data/2026-11-04.md（运维令10-31交付物v6例行复核+85M下载进度巡检+09:2x下载巡检,共19轮,详见日文件）
> 📦 唤醒1117-1160 原文已归档 → daily-memories-data/2026-11-04.md（运维令10-31交付物v6例行复核+85M下载进度巡检,共44轮,详见日文件）
> 📦 唤醒1107-1116 原文已归档 → daily-memories-data/2026-11-03.md（运维令10-31交付物v5例行复核+85M下载进度巡检+HF链接真实性抽检7个数据集HTTP 200全PASS,共10轮,详见日文件）

> 📦 唤醒1065-1106 原文已归档 → daily-memories-data/2026-11-03.md（运维令10-31交付物v4-v5例行复核+85M下载进度巡检,共42轮,详见日文件）
> 📦 唤醒1030-1063 原文已归档 → daily-memories-data/2026-10-31.md（运维令10-31报告v3-v4复核+85M下载进度巡检,详见日文件）
> 📦 唤醒833-1023 原文已归档 → daily-memories-data/2026-10-30.md ~ 2026-10-31.md（例行巡检+85M字节增长复核,详见日文件）
## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。
### ①-⑧ 已归档（详见 `daily-memories-data/2026-10-06.md`）

| # | 主题 | 结论 | 日期 |
|:--|:--|:--|:--|
| ① | SFT-2605 重下 | ✅ 1504 jsonl / 318.99 GB，与 HF 官方清单逐字节一致 | 10-02 |
| ②-④ | D-CLEAN-1/2/3 | ✅ 盘点 + 删除 servers(974G)+nemo R1(310G)+laion(7.8G)+pip(3.3G) ≈1.3T；nemo R2 ckpt 保留 | 10-03 |
| ⑤ | 下载白名单 | ✅ 停 en_v1_4，只下 l1_en_hq+zh+GPIC | 10-03 |
| ⑥-⑦ | D-CLEAN-4 + LLaVA ckpt | ✅ 盘点：本用户可回收 ≈11.4TiB(含 LLaVA-OV 22TiB iter ckpt)，待运维拍板 | 10-04 |
| ⑧ | LIT_IDEAS HTML | ✅ 产出 `LIT_IDEAS_2026-10-05.html`（52 entries/0 unverified/62% turnover），含成本专章+ISEDA投稿要求(4-6页) | 10-04 |
> 📦 §⑨ 配比实验可行性核查 + §⑩ 运维三问 + 旧状态头（2026-10-05~07）已归档 → `daily-memories-data/2026-10-10.md`（唤醒305归档）；**结论**：⑨GPU2-7当时被P-9.8/9.9占满(现已释放)⑩三问已答(GPIC无加速/base下载全满/BO波次锯齿非I/O)。需要时再读。

> 📦 §⑪ 分词5worker+85M线路（2026-10-24 用户质询）已归档 → daily-memories-data/2026-10-24.md；**结论**：Q1=5worker因串行+剩余shard少,升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT)。需要时再读。

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| R research（🎯 只答 §0 两问） | ✅ 完成（DATA_RESEARCH v1.1：LLM 够/走路线A；Vision 换 GPIC short 消截断） |
| R2 LLM 数据侧调研（任务书两项优先） | ✅ 完成（DATA_RESEARCH R2 节：8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B = base-en(86):code(10):math(4)；base 2.99TB 下载已启动） |
| R2 视觉侧调研（§0.4 去 HF 找通用图文对） | ✅ 完成（DATA_RESEARCH R2-视觉侧：本地 12 源图像形态+≤77 实测 / 13 HF 候选其中 7 URL-only 淘汰 / 前 3 推荐 CC12M≈11M + Amshaker≈6M + LLaVA≈1.15M，50 万→1800 万对 ×35，无需新下载） |
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | ✅ 完成（v0.3：536 任务 + NFKC/Unicode 归一化 + 8-gram 兜底 + **SFT 嵌套 jsonl 目录同闸扫描**，全快照正控 100%） |
| phase1 validate（完整性校验） | 🟡 校验脚本已备（validate_data.py），全量跑待下载完成后 |
| phase2 text（通用文本 .bin/.idx） | 🟡 分词打包 wrapper 已备（preprocess_text.sh + 污染闸门），跑待下载完成后 |
| phase3 domain（EDA 领域语料排查） | 🚫 **已取消**（运维 2026-10-01 夜：评测 prompt 由 docstring 生成、与语料天然同源，入库无意义）；但 EDA-Eval 158 任务黑名单红线**依然有效、继续执行** |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [x] ~~EDA API 知识库能否导出纯文本~~ → **已确认可行**：`eda_fastmcp/docs/` 本就是 md/json 纯文本（≈45MB，见 DATA_LEDGER §5）。
- [x] ~~EDA 语料入库授权~~ → **整条线已取消**（运维 2026-10-01 夜）：评测 prompt 由 docstring 生成、与语料天然同源，"把测试集放进训练集"无意义 → phase3_domain 不再调研/入库。**但 EDA-Eval-PyAether 158 任务黑名单红线照常执行。**
- [x] ~~内部培训材料 / 脱敏 CAD 案例能否用于训练~~ → 随 phase3_domain 一并取消。
- [ ] 多模态下载预计完成时间
- [x] ~~`UltraData-SFT-2605/-Agent-2609` 具体存储格式~~ → **已实测**：Agent-2609 = **jsonl**（50 shard / 51 GiB，2GB/shard）；**2605 = 落盘为空**（仅 179 个 `.lock` 缓存文件 / 22.4KiB，无数据，需重下）
- [x] ~~`UltraData-SFT-2605` 重新下载~~ → **✅ 已下满并核验一致（2026-10-02 唤醒 37）**：落盘 **1504 jsonl / 318,990,252,711 B = 318.99GB（297.08 GiB）**，`.incomplete` = 0，**与 HF 官方清单（1504 文件 / 318,990,252,711 B）逐字节完全一致**；逐子目录 `no_think` 855✓（CG 50/Code 300/IF 20/Kn 80/Math 300/ML-Kn 50/ML-Math 55）+ `think` 649✓（CG 50/Code 279/IF 20/Kn 50/Math 250）。token `hf_lqLxH…`（用户 foamliu）。

> 📦 旧流水（唤醒111-145, S0a训练+分词+kill改道全程）已归档 → `daily-memories-data/2026-10-05.md` 及 `2026-10-06.md`
> 关键结论：①base分词22.05B tok✅ ②SFT-2605 20.97B+Agent-2609 全4shard✅ ③S0a 2.2B单臂浪费~100 GPU·h→改道proxy BO搜索 ④proxy模型92.7M(d=512/L=14)标定s/step=1.5s ⑤smoke test✅

> 📦 §s_step归因实验（2026-10-06）已归档 → `daily-memories-data/2026-10-06.md`；**结论**：MBS=16使s_step 1432ms→166ms(8.6×),overhead-bound,D=0.5B/trial→205trial/24h。需要时再读。
## �