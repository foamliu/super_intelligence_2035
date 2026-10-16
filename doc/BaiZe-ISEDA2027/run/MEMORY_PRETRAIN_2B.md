# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

## 当前状态
- STAGE: **🚀 Xmodel-2.5 80B decay v2 训练 RUNNING**（01:20 启动, step 920/19980, loss 1.897, ~297.4K tok/s 稳态, ETA ~63h）。起点=step_532000 + BaiZe 80B(SFT64:L3:24:code8:math4) + Muon。**seq=3712/GBS=960/MBS=4/DP=8/总步19980=71.2B tok**。chunked CE + compile(default) + no_sync(default)。目标：14集超越 Xmodel-2.5 final (CS8 65.40%/CX 32.90%)。
  - PHASE: **decay80b_v2** — Xmodel-2.5 80B decay v2 训练中（01:18 启动, MBS=4+chunked CE）。8×H100 全占满（97-100% util, 51.7GB/卡）。train_log: step920 loss=1.8969 lr=1.36e-3(衰减中) tok/s=297.4K(稳态~299K)。📦 体积：TASK=26.2KB ✅ / MEMORY=29.7KB ✅。
  - ERROR_COUNT: 0
  - 轮询状态：8 GPU 全占满 — v2 训练健康运行中（torchrun PID 3753642, 01:18 启动, et~184min 无崩溃环, 0 NaN, 0 error）。→ **下一步**：每唤醒监控 step/loss/ETA；save_interval=2000（首个 ckpt@2000 ≈ ~08:00）。
  > 📦 **[已归档] #476 流水（2026-10-17 ~03:48, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step740 loss1.8562 tok/s297.1K 健康, et=148min 无崩溃环。需要时再读。**
  - 🔧 **本唤醒推进 = #478（2026-10-17 ~04:24, 🩺 v2 训练监控）**：① **训练健康**：step920 loss=1.8969 lr=1.36e-3(衰减中) tok/s=297.4K(稳态~299K)，last10 波动 1.67~2.15(缓降)，t_data=0.5ms≈0%/fwd_bwd=391.7ms≈99%/opt=152ms≈1%，8卡 97-100% util/51.7GB，0 NaN/0 error，et=184min 无崩溃环。② ETA：11.92s/step → 剩 19060 步 ≈63.1h → ETA 10-19 ~19:30；首 ckpt@2000≈08:00(还~3.6h)。③ **下一步**：继续每唤醒监控 step/loss/ETA。WAITING=1。
  > 📦 **[已归档] #477 流水（2026-10-17 ~03:52, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step760 loss1.8031 lr1.42e-3 tok/s297.1K 健康, et=152min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #475 流水（2026-10-17 ~03:20, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step600 loss1.967 tok/s296.7K 健康, et=122min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #474 流水（2026-10-17 ~02:48, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step440 loss2.0914 tok/s296.1K 健康, et=88min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #472 流水（2026-10-17 ~02:16, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step280 loss2.11 tok/s294.9K 健康, et=57min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #471 流水（2026-10-17 ~01:40, 🩺 v2 训练监控 + TASK 归档）→ daily-memories/2026-10-17.md；结论：v2 01:20 起训健康, TASK 37.1→26.8KB 归档4块。需要时再读。**
  > 📦 **[已归档] #470 流水（2026-10-17 ~01:20, 🔧 chunked CE 双 bug 修复 + v2 正式起训）→ daily-memories/2026-10-17.md；结论：label double-shift + μP logit scale=1/6 两 bug 修复，A0–A5 完成，MBS4+chunked CE 与 MBS2 HF 吞吐等价~299K，v2 01:20 起训。需要时再读。**
  > 📦 **[已归档] #469 流水（2026-10-16 ~21:13, 🩺 80B decay 监控·训练健康）→ daily-memories/2026-10-16.md；结论：step330 loss1.451 lr1.58e-3 183Ktok/s ETA~5.0天, 8卡全占健康。后续 00:24 step430 崩溃。需要时再读。**
  > 📦 **[已归档] #468 流水（2026-10-16 ~20:24, 🩺 80B decay 监控·训练健康）→ daily-memories/2026-10-16.md；结论：step190 loss1.599 lr1.63e-3 183Ktok/s ETA~5.0天, 8卡全占健康(et=72min无崩溃环)。需要时再读。**
  > 📦 **[已归档] #467 流水（2026-10-16 ~20:12, 🩺 80B decay 监控·训练健康）→ daily-memories/2026-10-16.md；结论：step160 loss1.86 lr1.65e-3 183Ktok/s ETA~5.0天, 运维核查闭环(非崩溃重启环)。需要时再读。**
  > 📦 **[已归档] #466 流水（2026-10-16 ~19:38, 🚀 80B decay 起训核查）→ daily-memories/2026-10-16.md；结论：训练19:14起训RUNNING, config核对✅(seq4096/GBS960/MBS2/DP8/20346步/TensorParallelMuon/数据SFT64:L3 24:code8:math4), tokenizer 128K↔129K remap(id≥128815→eos)已处理。需要时再读。**
  > 📦 **[已归档] #465 流水（2026-10-16 ~12:30, 📋 decay 80B 计划书确认 + TASK 归档 v5+proxy）→ daily-memories/2026-10-16.md；结论：计划书 36KB 确认 6 点全 ✅, TASK 34.3→26.9KB。需要时再读。**
  > 📦 **[已归档] #463 流水（2026-10-16 ~09:27, 🔄 keepalive 心跳·v5报告确认·状态无变化）→ daily-memories/2026-10-16.md；结论：keepalive, v5报告确认全口径✅, 8GPU空闲, 无新指令。需要时再读。**
  > 📦 **[已归档] #462 流水（2026-10-16 ~08:17, 🔄 keepalive 心跳·v5报告复核·状态无变化）→ daily-memories/2026-10-16.md；结论：keepalive, v5报告复核全口径✅, 8GPU空闲, 无新指令。需要时再读。**
  > 📦 **[已归档] #461 流水（2026-10-16 ~07:07, 🔄 keepalive 心跳·状态无变化）→ daily-memories/2026-10-16.md；结论：keepalive, v5报告确认, 8GPU空闲, 无新指令。需要时再读。**
  > 📦 **[已归档] #459 流水（2026-10-16 ~04:49, 🔄 keepalive 心跳·状态无变化）→ daily-memories/2026-10-16.md；结论：keepalive, v5报告确认, 8GPU空闲, 无新指令。需要时再读。**
  > 📦 **[已归档] #458 流水（2026-10-16 ~03:00, 🔧 v5 报告表格数修正 13→6）→ daily-memories/2026-10-16.md；结论：v5报告从13表修正到6表(满足≤6硬口径), 42.8KB/6表/1SVG/6节。需要时再读。**
  > 📦 **[已归档] #457 流水（2026-10-16 ~02:26, 🔄 keepalive 心跳·v5报告验证·状态无变化）→ daily-memories/2026-10-16.md；结论：v5报告确认在盘, 8GPU空闲, 无新指令。需要时再读。**
  > 📦 **[已归档] #456 流水（2026-10-16 ~01:23, 🔄 keepalive 心跳·git 同步修复·状态无变化）→ daily-memories/2026-10-16.md；结论：git pull 修复 + v5报告确认在盘 + 8 GPU 空闲。需要时再读。**
  > 📦 **[已归档] #455 流水（2026-10-16 ~00:10, 📊 Xmodel-2 s1 eval 收集 + scaling report 更新）→ daily-memories/2026-10-16.md；结论：s1 4 ckpt eval 全完成, scaling_report.html 重新生成(14KB, 2 SVG), BaiZe 44B CS8=49.21% ≈ XM2 157B CS8=50.31% (差1.10pp)。需要时再读。**
  > 📦 **[已归档] #454 流水（2026-10-15 ~22:30, 📝 v5 预训练计划书完成·44KB·6节）→ daily-memories/2026-10-15.md；结论：v5 报告 44KB commit fc0a292b, 5问速答+三方对照+推荐策略+配比实验+风险+附录。需要时再读。**
  > 📦 **[已归档] #453 流水（2026-10-15 ~21:21, ⚡ Xmodel-2 s1 并行 eval 启动·3 BBH 并行+CS8/Complex5 并行·预计 12h→3h）→ daily-memories/2026-10-15.md；结论：s1/10K CS8=46.65% vs BaiZe P-8 CS8=49.21% → BaiZe +2.56pp 早期学习不弱于 Xmodel-2。需要时再读。**
  > 📦 **[已归档] #452 流水（2026-10-15 ~19:58, 📊 Xmodel-2 s1 re-eval 启动 + TASK 归档 + collect_eval_summary.py 创建）→ daily-memories/2026-10-15.md；结论：s1 4 ckpt 下载✅, s1/10K CS8✅(trust_remote_code=True生效), 顺序脚本启动。需要时再读。**
  > 📦 **[已归档] #451 流水（2026-10-15 ~18:36, 📊 Xmodel-2.5 final 14-dataset 完成 + scaling report 更新）→ daily-memories/2026-10-15.md；结论：Xmodel-2.5 final CS8=65.40%/CX=32.90%, BBH=25.86%, report 已重新生成。需要时再读。**
  > 📦 **[已归档] #450 流水（2026-10-15 ~15:30, 📊 14-benchmark eval + Xmodel scaling 对比·P-8 final + Xmodel-2.5 step_2000/4000 + scaling report生成）→ daily-memories/2026-10-15.md；结论：P-8 final 14集✅, Xmodel-2.5 history CS8✅, report✅, 下载进行中。需要时再读。**
  > 📦 **[已归档] #449 流水（2026-10-15 ~07:51, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #446 流水（2026-10-15 ~06:12, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #444 流水（2026-10-15 ~05:08, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #442 流水（2026-10-15 ~04:04, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #441 流水（2026-10-15 ~03:32, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #440 流水（2026-10-15 ~03:01, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #439 流水（2026-10-15 ~02:29, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #437 流水（2026-10-15 ~01:26, 🔄 keepalive 心跳·状态无变化·8 GPU 全空闲·无新运维指令）→ daily-memories/2026-10-15.md；结论：keepalive, 无变化。需要时再读。**
  > 📦 **[已归档] #435 流水（2026-10-15 ~00:10, ✍️ F2 论文回填·P-8生产结果写入abstract+§4_full_train·13pp 0-error）→ daily-memories/2026-10-15.md；结论：F2 完成(3处修改+新增subsection), 13pp 0-error, 所有待办闭合。需要时再读。**
  > 📦 **[已归档] #434 流水（2026-10-14 ~23:45, 📦 任务书归档·v4 plan+decay fix 两块→ARCHIVE·TASK 35.1KB→28.0KB ✅）→ daily-memories/2026-10-14.md；结论：TASK 归档完成, 两项最高优先运维指令(v4报告+decay fix)均已完成。需要时再读。**
  > 📦 **[已归档] #433 流水（2026-10-14 ~22:30, 📋 v4 正式训练计划报告·47KB·3SVG·11表·14源精确token/int32/密度归因/D-scan/SFT过采样）→ daily-memories/2026-10-14.md；结论：v4 报告完成, 逐源精确token(577.98B .bin), D-scan(avg=11.9177×logD+33.87, R²=0.964), 诚实条款4级。需要时再读。**
  > 📦 **[已归档] #432 流水（2026-10-14 ~21:45, 🏁 P-8 decay FIX 完成·final ckpt@1149·LR 1.85e-5·SEQ→4096·8 GPU 释放）→ daily-memories/2026-10-14.md；结论：decay fix 1149步 loss 1.914→1.357, LR 1e-3→1.85e-5 WSD线性, final ckpt@1149 ✅, 全程 44.4B tok/412 GPU·h/0 NaN。需要时再读。**
  > 📦 **[已归档] #431 流水（2026-10-14 ~21:09, P-8 decay FIX 监控·step1070/1149 · LR 8.46e-5 精确衰减 · loss 1.358 · ckpt@1000 已存）→ daily-memories/2026-10-14.md；结论：step1070 LR=8.46e-5衰减中, loss 1.358, ckpt@1000已存, ETA~23min。需要时再读。**
  > 📦 **[已归档] #430 流水（2026-10-14 ~20:36, P-8 decay FIX 监控·step950/1149 · ✅ LR 1.98e-4 精确衰减 · loss 1.376 新低 · 0 NaN）→ daily-memories/2026-10-14.md；结论：step950 LR=1.978e-4衰减中, loss 1.376新低, ckpt@500已存。需要时再读。**
  > 📦 **[已归档] #429 流水（2026-10-14 ~20:01, P-8 decay FIX 监控·step840/1149 · ✅ LR 3.02e-4 精确衰减 · loss 1.393 新低 · 0 NaN）→ daily-memories/2026-10-14.md；结论：step840 LR=3.02e-4衰减中, loss 1.393新低, ckpt@500已存。需要时再读。**
  > 📦 **[已归档] #428 流水（2026-10-14 ~19:32, P-8 decay FIX 监控·step730/1149 · ✅ LR 4.05e-4 精确衰减 · loss 1.407 新低 · 0 NaN）→ daily-memories/2026-10-14.md；结论：step730 LR=4.05e-4衰减中, loss 1.407新低, ckpt@500已存。需要时再读。**
  > 📦 **[已归档] #427 流水（2026-10-14 ~18:57, P-8 decay FIX 监控·step620/1149 · ✅ LR 5.09e-4 精确衰减 · loss 1.432 新低 · 0 NaN）→ daily-memories/2026-10-14.md；结论：step620 LR=5.09e-4衰减中, loss 1.432新低, ckpt@500已存。需要时再读。**
  > 📦 **[已归档] #426 流水（2026-10-14 ~18:23, P-8 decay FIX 监控·step500/1149 · ✅ 首个 ckpt@500 已存 · LR 6.22e-4 衰减 ✅ · loss 1.462 新低 · 0 NaN）→ daily-memories/2026-10-14.md；结论：step500 LR=6.22e-4衰减中, loss 1.462新低, ckpt@500已存4.2G。需要时再读。**
  > 📦 **[已归档] #425 流水（2026-10-14 ~17:50, P-8 decay FIX 监控·step390/1149 · LR 7.26e-4 精确衰减 ✅ · loss 1.495 新低 · 0 NaN）→ daily-memories/2026-10-14.md；结论：step390 LR=7.26e-4衰减中, step370 loss=1.495新低, 0 NaN。需要时再读。**
  > 📦 **[已归档] #422 流水（2026-10-14 ~15:47, 🔧 P-8 decay LR 未衰减根因定位+修复+重跑 · finetune mode · LR warmup 确认 ✅）→ daily-memories/2026-10-14.md；结论：根因=resume时scheduler state不加载+全局step=9441→decay区到不了→LR恒1e-3; 修复=--finetune flag(step=0,fresh scheduler); 新脚本baize_p8_decay_fix.sh启动, step10 LR=1.0e-4 warmup ✅。需要时再读。**
  > 📦 **[已归档] #421 流水（2026-10-14 ~14:29, P-8 decay 监控·step9710 · loss 1.57 缓慢下降 · LR 未衰减持续确认 · MEMORY 归档瘦身）→ daily-memories/2026-10-14.md；结论：step9710 loss=1.57 趋稳, LR 全程 1e-3 未衰减(27个log点), MEMORY 归档~12KB。需要时再读。**
  > 📦 **[已归档] #420 流水（2026-10-14 ~13:54, P-8 decay 监控·step9580 · SFT annealing loss 1.71 趋稳 · ⚠️ LR 未衰减发现）→ daily-memories/2026-10-14.md；结论：step9580 loss=1.71 趋稳, LR 全程 1e-3 未衰减(27个log点确认), NeMo WSD resume optimizer state 覆盖调度器。需要时再读。**
  > 📦 **[已归档] #419 流水（2026-10-14 ~13:06, 🔄 decay 切换执行 · stable 停止 · decay 启动 · 从 ckpt@9441 resume SFT blend ✅）→ daily-memories/2026-10-14.md；结论：stable 停止@9441, decay 启动@13:10:15, resume ckpt@9441 SFT blend, PID 1743529/1744126, GPU 52-55GB 77-100%util。需要时再读。**
  > 📦 **[已归档] #418 流水（2026-10-14 ~12:31, P-8 监控·step9370 · loss 新低 2.462020 · decay 切换≈21min）→ daily-memories/2026-10-14.md；结论：step9370 loss min=2.462020@9330, decay 切换预案就绪。需要时再读。**
  > 📦 **[已归档] #416 流水（2026-10-14 ~11:23, P-8 监控·step9130 · loss 新低 2.470327）→ daily-memories/2026-10-14.md；结论：step9130 loss min=2.470327@9070 新低, decay 切换≈1.5h, decay脚本就绪。需要时再读。**
  > 📦 **[已归档] #415 流水（2026-10-14 ~10:45, P-8 监控·step8990 + TASK归档 + 4094→4096记录修正）→ daily-memories/2026-10-14.md；结论：step8990 loss min=2.473512新低, TASK归档至30.6KB, 4094→4096口径修正完成。需要时再读。**
  > 📦 **[已归档] #414 流水（2026-10-14 ~10:05, ✍️ 论文改稿执行 H1-H4+S1-S10 + P-8 监控·step8850）→ daily-memories/2026-10-14.md；结论：论文改稿全完成 H1-H4+S1-S10 (commit 75963f3d, 11pp 0-error ✅)。需要时再读。**
  > 📦 **[已归档] #413 流水（2026-10-14 ~09:00, 📝 论文审视 HTML + P-8 监控·step8510）→ daily-memories/2026-10-14.md；结论：4项🔴硬伤+10项🟠建议+3项🟢可回填报告已交付(26.5KB)，未改.tex。需要时再读。**
  > 📦 **[已归档] #412 流水（2026-10-14 ~08:26, P-8 AdamW 监控·step8510 · loss 2.4911 min=2.481677 81%完成）→ daily-memories/2026-10-14.md；结论：step8510 loss=2.486300, last10 avg=2.4911, min=2.481677@8400, ckpt@8392 latest, v3报告在origin/main。需要时再读。**
  > 📦 **[已归档] #411 流水（2026-10-14 ~07:50, P-8 AdamW 监控·step8380 · loss last10 avg=2.4925 min=2.485127 新低 79.9% 完成）→ daily-memories/2026-10-14.md；结论：step8380 loss=2.493447, last10 avg=2.4925, min=2.485127@8330, ckpt@7343→8392 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #410 流水（2026-10-14 ~07:17, P-8 AdamW 监控·step8260 · loss last10 avg=2.4979 min=2.489893 新低 78.7% 完成）→ daily-memories/2026-10-14.md；结论：step8260 loss=2.497740, last10 avg=2.4979, min=2.489893@8220, ckpt@7343 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #409 流水（2026-10-14 ~06:41, P-8 AdamW 监控·step8140 · loss last10 avg=2.5015 min=2.494125 新低 77.7% 完成）→ daily-memories/2026-10-14.md；结论：step8140 loss=2.506750, last10 avg=2.5015, min=2.494125@8120, ckpt@7343 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #407 流水（2026-10-14 ~05:32, P-8 AdamW 监控·step7890 · loss last10 avg=2.512 min=2.5048 新低 75.1% 完成）→ daily-memories/2026-10-14.md；结论：step7890 loss=2.508890, last10 avg=2.512, min=2.504840@7870, ckpt@7343 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #406 流水（2026-10-14 ~04:59, P-8 AdamW 监控·step7770 · loss last10 avg=2.514 min=2.5081 新低 74.1% 完成）→ daily-memories/2026-10-14.md；结论：step7770 loss=2.5098, last10 avg=2.514, min=2.5081@7710, ckpt@7343 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #405 流水（2026-10-14 ~04:23, P-8 AdamW 监控·step7650 · loss last10 avg=2.520 min=2.5132 新低 73.0% 完成）→ daily-memories/2026-10-14.md；结论：step7650 loss=2.5132, last10 avg=2.520, min=2.5132, ckpt@7343 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #403 流水（2026-10-14 ~03:17, P-8 AdamW 监控·step7410 · loss last10 avg=2.525 min=2.5186 新低 70.6% 完成）→ daily-memories/2026-10-14.md；结论：step7410 loss=2.5268, last10 avg=2.525, ckpt@7343 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #402 流水（2026-10-14 ~02:42, P-8 AdamW 监控·step7290 · loss last10 avg=2.529 min=2.519 69.4% 完成）→ daily-memories/2026-10-14.md；结论：step7290 loss=2.5318, last10 avg=2.529, ckpt@6294 latest, v3 报告在 origin/main。需要时再读。**
  > 📦 **[已归档] #401 流水（2026-10-14 ~02:10, P-8 AdamW 监控·step7172 · loss last10 avg=2.526 min=2.504 新低 68.4% 完成）→ daily-memories/2026-10-14.md；结论：step7172 loss=2.5441, last10 avg=2.526, v3 报告确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #399 流水（2026-10-14 ~01:00, P-8 AdamW 监控·step6920 · loss last10 avg=2.543 min10=2.5375 新低 65.97% 完成）→ daily-memories/2026-10-14.md；结论：step6920 loss=2.5375, last10 avg=2.543, min10=2.5375, v3 报告确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #398 流水（2026-10-14 ~00:25, P-8 AdamW 监控·step6800 · loss last10 avg=2.553 持续缓降 64.8% 完成）→ daily-memories/2026-10-14.md；结论：step6800 loss=2.5444, last10 avg=2.553, min10=2.540, v3 报告确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #397 流水（2026-10-13 ~23:49, P-8 AdamW 监控·step6680 · loss last10 avg=2.552 持续缓降 63.7% 完成）→ daily-memories/2026-10-13.md；结论：step6680 loss=2.5488, last10 avg=2.552, v3 报告 commit 280adeac 确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #396 流水（2026-10-13 ~23:12, P-8 AdamW 监控·step6550 · loss last10 avg=2.560 持续缓降 62.4% 完成）→ daily-memories/2026-10-13.md；结论：step6550 loss=2.5542, last10 avg=2.5600, v3 报告 commit 280adeac 确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #394 流水（2026-10-13 ~21:00, 📋 v3 正式训练计划重做(实盘盘点口径) · 20.1KB · P-8 AdamW step6251）→ daily-memories/2026-10-13.md；结论：v3 报告 20.1KB ✅ commit 280adeac, 弃300B改实盘9.81TB/2232B token。需要时再读。**
  > 📦 **[已归档] #393 流水（2026-10-13 ~19:30, v2 正式训练计划 300B · 被否决→v3）→ daily-memories/2026-10-13.md；结论：v2 30.4KB(300B基准) 被用户否决(CSDN无一手依据)。需要时再读。**
  > 📦 **[已归档] #392 流水（2026-10-13 ~18:35, P-8 监控·step5568 · loss min50=2.566 新低 53.1%）→ daily-memories/2026-10-13.md；结论：step5568 loss=2.578, min50=2.566, ckpt@5245, next@6294。需要时再读。**
  > 📦 **[已归档] #390 流水（2026-10-13 ~17:03, P-8 AdamW 监控·step5240 · loss 2.616 50%完成）→ daily-memories/2026-10-13.md；结论：step5240/10490 loss=2.6165 新低, last10 avg=2.623, ckpt@5245保存, next@6294。需要时再读。**
  > 📦 **[已归档] #389 流水（2026-10-13 ~16:28, P-8 AdamW 监控·step5117 · loss 持续下降 last100 avg 2.629）→ daily-memories/2026-10-13.md；结论：step5117/10490 loss=2.603 stable健康, next ckpt@5245 ~20min。需要时再读。**
  > 📦 **[已归档] #349~#388 流水（2026-10-12 ~ 2026-10-13, 共 ~40 条, P-8 AdamW warmup+stable 段监控）→ daily-memories/2026-10-12.md / 2026-10-13.md 各日文件；结论：warmup 524 步 ✅, stable 段 step610→9441 loss 3.734→2.456 持续下降健康, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049→2098→3147→4196→5245→6294→7343→8392→9441。需要时再读各日文件。**

## 🗣️ 运维问答 · 2026-10-09（补测对比报告 · 先报后跑门控）

> **运维令**：补测 + 中文对比报告：BaiZe-Hybrid 2.220B ⚔ 参数匹配 Dense Llama，SGLang，ctx 持续 ×2 直到 hybrid OOM。门控：先报「参数匹配方案 + 测试矩阵 + ETA + 占用卡」，再开跑。

### ① 参数匹配方案

**主对手臂 = Dense Llama 36L（随机初始化）**
- 构建：复用 `p3_dense`（MiniCPM5-2B, 42L）的架构配置，**仅减层数 42→36**，使总参数对齐 hybrid。
- 架构配置（`config.json` 将照此生成）：

| 参数 | 值 | 来源 |
|:--|:--|:--|
| `architectures` | `LlamaForCausalLM` | 标准 Llama |
| `vocab_size` | 129,408 | 与 hybrid/dense 同 tokenizer |
| `hidden_size` | 2,048 | 同 p3_dense |
| `intermediate_size` | 6,144 | 同 p3_dense（SwiGLU 3×H） |
| `num_hidden_layers` | **36**（从 42 减 6） | 调此值对齐参数 |
| `num_attention_heads` | 16 | 同 p3_dense |
| `num_key_value_heads` | 2 | 同 p3_dense（GQA） |
| `head_dim` | 128 | 同 p3_dense |
| `hidden_act` | silu | SwiGLU |
| `tie_word_embeddings` | false | 同 p3_dense |
| `max_position_embeddings` | 4096 | 同 p3_dense（推理时 SGLANG_ALLOW_OVERWRITE 扩展） |
| `rope_theta` | 5,000,000.0 | 同 p3_dense |

- **精确参数量**（Python 实算）：
  - Embedding: 129,408 × 2,048 = 265,090,048
  - LM head: 265,090,048（不 tie）
  - 每层 attn: q 4,194,304 + k 524,288 + v 524,288 + o 4,194,304 = 9,437,184
  - 每层 MLP: 3 × 2,048 × 6,144 = 37,748,736
  - 每层 norms: 2 × 2,048 = 4,096
  - 每层合计: 47,190,016
  - 36 层: 1,698,840,576
  - Final norm: 2,048
  - **总计: 2,228,897,792 = 2.229B**
  - **vs hybrid 2,220,268,032 = +0.389%（±1% 内 ✅）**
- ⚠️ **权重随机初始化**（`torch.randn` × `initializer_range=0.02`）—— 本次比的是**速度/显存**，与权重值无关；报告中将显式标注。
- tokenizer 文件直接复制 `p3_dense`（同 vocab=129,408）。

**参考臂 = p3_dense（MiniCPM5-2B, 2.512B, 42L）**：附录/脚注用，佐证「未做参数匹配时偏袒 dense 约 +13% 参数」。

**备选方案（若运维要求更紧匹配）**：L=35, kv_heads=4（匹配 hybrid 的 4 KV heads）→ 2,218,407,936 = −0.084%。但 KV cache 翻倍（kv=4 vs kv=2）会使 dense 更早 OOM，可能不是「公平」的解读。

### ② 测试矩阵

| 维度 | 取值 | 说明 |
|:--|:--|:--|
| **模型** | {hybrid 2.220B, **dense-matched 2.229B**, p3_dense 2.512B(ref)} | 主对比 = hybrid vs dense-matched |
| **ctx** | 128K→256K→512K→1M→2M→4M→8M（×2） | 持续 ×2 直到 **hybrid 自己 OOM** 才停 |
| **mem-frac** | {0.6, 0.85} | ≥0.6（旧 0.3 太低致 dense 假 OOM）；同 ctx 两臂同值 |
| **bs** | {1, 8} | 至少两档 |
| **gen_len** | 64 | 同 P-9.11 |
| **WARMUP** | 1 | 丢弃首请求（消除 CUDA kernel 编译冷启动） |
| **REPEATS** | 3（取 median） | 公平口径 |
| **per-B 归一化** | tok/s ÷ B | 报告中每格同时报原始和 per-B |

**SGLang flags（两臂一致，仅 hybrid 额外加 SSM dtype）**：
```
--mem-fraction-static {0.6|0.85}
--attention-backend flashinfer
--dtype bfloat16
--context-length {ctx}
--disable-radix-cache
SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
# hybrid 额外: --mamba-ssm-dtype float32
```
- 环境：`vllm` conda env（sglang 0.5.9），与训练 env 隔离。
- prompt 构造：tokenizer 精确计数（`len(tok(prompt))` = ctx − 128 safety margin），复用 `p911d_sglang_vram_bench.py` 的 `make_prompt_precise()`。
- 每格记录：prefill tok/s / TTFT / decode tok/s / e2e / 峰值 VRAM / pool tokens / prompt 实 token 数 / status(SERVED/OOM/TIMED_OUT)。

**已有数据可复用**：P-9.11-E 的 mem-frac=0.3 结果（`p911e_results/*.json`）作为**低 mem-frac 对照**附录，不作为主表数据（口径不同）。

**终止条件**：hybrid 在某 ctx × mem-frac 下 OOM/不可服务 → 该 mem-frac 的扫描到此 ctx 为止；但**另一 mem-frac 继续扫**直到也 OOM。两 mem-frac 都 OOM → 全停。

### ③ ETA

| 阶段 | 墙钟 | 说明 |
|:--|:--|:--|
| 创建随机 Dense 模型 | ~10 min | Python 脚本生成 config.json + safetensors + 复制 tokenizer |
| 128K–512K（3 ctx × 2 mf × 3 model × 2 bs） | ~1–2h | 低 ctx 每格 <1min，4–6 GPU 并行 |
| 1M（2 mf × 3 model × 2 bs） | ~1–2h | hybrid 1M prefill ~7min/req，dense 可能 OOM |
| 2M（2 mf × 2 model × 2 bs） | ~2–3h | hybrid 2M ~30min/req（P-9.11-F TTFT=427s@mf0.6） |
| 4M–8M（若 hybrid 存活） | ~2–3h | 4M 已知 TIMED OUT@mf0.85；8M 可能不可服务 |
| **合计** | **~6–10h** | 可跨多个唤醒分阶段完成 |

### ④ 占用卡

- **.29 GPU 0–7**（8×H100 80GB），**纯推理**（无训练、无重 I/O）。
- 同时活跃 2–4 个 SGLang server（每个占 1 GPU），其余 GPU 空闲。
- 🚫 不碰 .12（vision 节点）。
- 🚫 不启动 P-8、不改 P-5b recipe、不 kill watchdog。

### ⑤ Warmup 24× 归因（证据）

- **现象**：P-9.11-E hybrid 128K bs=1 prefill=1,591 tok/s（TTFT=79.1s）vs bs=8 prefill=447,796 tok/s（TTFT=2.25s）→ **281× 差距**。
- **归因**：bs=1 是 server 启动后**第一个请求** → SGLang/flashinfer 首次执行时触发 CUDA kernel JIT 编译 + cuBLAS handle 初始化 + memory pool 首次分配 → **冷启动开销 ~77s**。bs=8 紧随其后，kernel 已编译 → 正常速度。
- **证据**：(a) 2M ctx 的结果（`p911e_hybrid_ctx2097152_gpu5.json`）TTFT=8.49s/prefill=237,575 tok/s → 比 128K bs=1 快 150× → **不是 ctx 越大越慢**，而是首请求冷启动；(b) dense 128K bs=1 TTFT=23.97s 也偏慢（但比 hybrid 好，因 dense 无 SSM kernel 需编译）。
- **修正**：本次 **WARMUP=1** 丢弃首请求 → REPEATS=3 均为 warm 状态 → 消除冷启动偏差。旧 P-9.11-E 的 bs=1 数据**不应作为公平对比基线**（无 warmup）。

### ⑥ 下一步（等运维确认后执行）

1. 创建随机初始化 Dense Llama 36L → `hf_checkpoints/dense_matched_2.22b/`
2. 落地 SGLang 基准脚本（复用 `p911d_sglang_vram_bench.py`，加 WARMUP/REPEATS）
3. 分阶段跑：先 128K–512K（快速验证）→ 1M–2M → 4M+（直到 hybrid OOM）
4. 生成 `report_pretrain_baize_vs_dense_fair_zh.html`（中文，≤5 表，内联 SVG）

---

> 📦 **[已归档] 🗣️ 运维问答「提 3 个实验 idea」（2026-10-09, #251 已交付）→ daily-memories/2026-10-09.md；结论：3 idea 按价值排序（①P-8彩排续跑 ②P-8 44B下限档 ③R3配比迁移A/B），建议「立即起P-8」。需要时再读。**

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- transformer_engine 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8 / megatron-core 0.16.1 / mamba-ssm 2.2.6.post3（P-9.4 已核实，与任务书预期一致）。
- 结果主文件：R2=`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`；Round1=`EXPERIMENTS_PRETRAIN_2B.md` + `BAIZE_PRETRAIN_RESULT.html` + `ISEDA2027/4_llm_pretrain.tex`。
- ckpt：p3_hybrid/iter_0005000 → **HF nemotron_h ✅**（`nemo_experiments/p3_hybrid/hf_iter_5000/`，323 keys, 2.220B）+ p3_dense/iter_0005000 → **HF Llama ✅**（`nemo_experiments/p3_dense/hf_iter_5000/`，381 keys, 2.512B）；原始 mcore distcp @ `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`。

## GPU / 进程
- 主训练 10.239.2.29（8×H100 GPU0~7）：P-5b ✅ 已结束；P-9.1~P-9.7 全 ✅ 定稿；P-9.8 ✅ / P-9.9 ✅ / P-9.10 ①②③ ✅ / **P-5b 8-set eval ✅ COMPLETE**（GPU0-1 已释放）；**⭐ 全 8 GPU 空闲**（data agent @08:06 kill S0a → GPU2-7 释放；proxy 标定尚未起跑）；**P-9.11 ① HF 转换 ✅ BOTH DONE**（p3_hybrid→nemotron_h + p3_dense→Llama，待 sglang 起服）。
- watchdog `baize_pretrain_loop.sh` PID 1391466 必须 7×24 存续，🚫 绝不 kill。
- P-9（P-9.1 ✅ / P-9.2 ✅ / P-9.3 ✅ / P-9.4 ✅ / **P-9.5 ✅ COMPLETE** — 崩溃修复 + 5-way 归因 + HTML / P-9.6①② ✅ / P-9.7 ✅ / P-9.8 ✅ COMPLETE → delayed FP8 可用于 P-8 / **P-9.9 ✅ COMPLETE → tensorwise T1/T4 FAIL → P-8 沿用 delayed** / **P-9.10 ① ✅ sglang ✅ 可用(vllm env) [第109次更正] → eager 下界✅已测 + sglang 上界待 HF 转换补测，② ✅ COMPLETE eager 下界 H1✅H2❌H3❌H4✅**）；🚫 不对 live 长跑做 nsys/ncu attach。
