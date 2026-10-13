# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

## 当前状态
- STAGE: **🟢 P-8 AdamW 从零训练中（step6920/10490, 65.97%, stable 段 71.7%, LR=1e-3 恒定, loss last10 avg=2.543 min10=2.5375 ✅, ckpt@1049+2098+3147+4196+5245+6294 ✅, next@7343 ~423步 ≈2.0h）** — 用户令停 dist_muon（step8490 loss=2.623 发散）→ 换回 AdamW 从零重启。dist_muon 版已停, 8 个 ckpt保留为发散证据在 `p8/checkpoints/`（34GB）。**新 run = `p8_adamw`**（独立 ckpt 目录, ~25GB）。脚本 `baize_p8_adamw_train.sh` 运行中（torchrun PID 771300 / bash PID 771288, etimes~117000s≈32.5h）。warmup 524 → stable 8917 → decay 1049 = 10490 步 / ~2.0 天。AdamW 健康：loss 3.98→2.646(4660)→2.606(5360)→2.572(6251)→2.543(6920 last10) 平滑下行, min10=2.5375(step6920), grad_norm 0.11-0.15 稳定, 0 NaN, ~247K tok/s ✅。**next ckpt@7343**（~423步 ≈2.0h）。
  - PHASE: **p8_adamw_stable_step6920** — P-8 AdamW **stable 段** 71.7%（6920/10490 步, ~29.0B/44B token, stable 进度 6396/8917=71.7%）。WSD(warmup=524): ✅ warmup 0→524 已完成 → **stable 524→9441（当前6920, LR=1.0e-3 恒定 ✅）** → decay 9441→10490。✅ ckpt@1049+2098+3147+4196+5245+6294 均已保存（~4.2GB each, latest=6294, ~25GB total）。next ckpt@7343（~423步 ≈2.0h）/ decay 切换@9441（~2521步 ≈11.9h）。GPU 8 卡 54-57GB 97-100%util。torchrun 活跃（PID 771300/771288, etimes~117000s≈32.5h）。⚠️ dist_muon ckpt 8 个在 `p8/checkpoints/`（34GB 保留为证据）。新 ckpt 写入 `p8_adamw/checkpoints/`。🚫绝不 kill watchdog loop(PID 1391466)。
  - ERROR_COUNT: 0
  - 轮询状态：30min 长轮询。**全 8 GPU 占用**（.29, 54-57GB/card 97-100%util, AdamW 训练, PID 771288/771300）。⚠️ sklearn .pth 已禁用。decay 切换预案：step9441 ckpt 保存后 → `pkill -f pretrain_launcher.*p8_adamw` → 等 30s → `setsid bash baize_p8_decay.sh &`。📦 体积：TASK=32323B(31.6KB) ✅ ≤32KB / MEMORY≈27KB ✅ ≤32KB（无需归档）。🚫绝不 kill watchdog loop(PID 1391466)。⚠️ /nas_train 85% used(33T free) ✅。
  - 🩺 **本唤醒推进 = #399（2026-10-14 ~01:00, P-8 AdamW 监控·step6920 · loss last10 avg=2.543 min10=2.5375 新低 65.97% 完成）**：① git fetch+status：up to date with origin/main, 无 behind/ahead（harness 线有未跟踪文件, 非本线, 不动）。② P-8 AdamW 监控：step6920/10490 (65.97%)，loss=2.5375(last, step6920), last10 avg=2.543, min10=2.5375(step6920 新低！), grad_norm 0.115-0.154 稳定, LR=1e-3 ✅, 0 NaN, 0 skipped, ~247K tok/s, step_time 16.8-17.4s, GPU 8卡 97-100%util 54-57GB, ~590 TFLOP/s/GPU。③ ckpt@6294 仍为最新, next@7343 ~423步≈2.0h, decay 切换@9441 ~2521步≈11.9h。④ 进程健康：torchrun PID 771300 etimes~32.5h, bash PID 771288。⑤ /nas_train 85% used(33T free) ✅, p8_adamw ckpt 25GB ✅。⑥ v3 报告(20.1KB, commit 280adeac)已在 origin/main ✅, 无新运维指令。⑦ 体积：TASK=32323B(31.6KB) ✅ / MEMORY≈27KB ✅。→ **下次唤醒**：① P-8 监控继续（ckpt@7343 应已保存, next@8392, decay 切换@9441 ~11.9h后）② 若有新运维指令则执行 ③ 体积自检。WAITING=1。
  > 📦 **[已归档] #398 流水（2026-10-14 ~00:25, P-8 AdamW 监控·step6800 · loss last10 avg=2.553 持续缓降 64.8% 完成）→ daily-memories/2026-10-14.md；结论：step6800 loss=2.5444, last10 avg=2.553, min10=2.540, v3 报告确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #397 流水（2026-10-13 ~23:49, P-8 AdamW 监控·step6680 · loss last10 avg=2.552 持续缓降 63.7% 完成）→ daily-memories/2026-10-13.md；结论：step6680 loss=2.5488, last10 avg=2.552, v3 报告 commit 280adeac 确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #396 流水（2026-10-13 ~23:12, P-8 AdamW 监控·step6550 · loss last10 avg=2.560 持续缓降 62.4% 完成）→ daily-memories/2026-10-13.md；结论：step6550 loss=2.5542, last10 avg=2.5600, v3 报告 commit 280adeac 确认在 origin/main。需要时再读。**
  > 📦 **[已归档] #394 流水（2026-10-13 ~21:00, 📋 v3 正式训练计划重做(实盘盘点口径) · 20.1KB · P-8 AdamW step6251）→ daily-memories/2026-10-13.md；结论：v3 报告 20.1KB ✅ commit 280adeac, 弃300B改实盘9.81TB/2232B token。需要时再读。**
  > 📦 **[已归档] #393 流水（2026-10-13 ~19:30, v2 正式训练计划 300B · 被否决→v3）→ daily-memories/2026-10-13.md；结论：v2 30.4KB(300B基准) 被用户否决(CSDN无一手依据)。需要时再读。**
  > 📦 **[已归档] #392 流水（2026-10-13 ~18:35, P-8 监控·step5568 · loss min50=2.566 新低 53.1%）→ daily-memories/2026-10-13.md；结论：step5568 loss=2.578, min50=2.566, ckpt@5245, next@6294。需要时再读。**
  > 📦 **[已归档] #390 流水（2026-10-13 ~17:03, P-8 AdamW 监控·step5240 · loss 2.616 50%完成）→ daily-memories/2026-10-13.md；结论：step5240/10490 loss=2.6165 新低, last10 avg=2.623, ckpt@5245保存, next@6294。需要时再读。**
  > 📦 **[已归档] #389 流水（2026-10-13 ~16:28, P-8 AdamW 监控·step5117 · loss 持续下降 last100 avg 2.629）→ daily-memories/2026-10-13.md；结论：step5117/10490 loss=2.603 stable健康, next ckpt@5245 ~20min。需要时再读。**
  > 📦 **[已归档] #388 流水（2026-10-13 ~16:00, P-8 AdamW 监控·step4966 + TASK 归档 37KB→29.9KB）→ daily-memories/2026-10-13.md；结论：step4966/10490 loss=2.66 stable健康, TASK 归档完成 37KB→29.9KB ✅。需要时再读。**
  > 📦 **[已归档] #387 流水（2026-10-13 ~15:09, 📋 正式训练计划 HTML 交付 · report_pretrain_formal_train_plan.html 27.9KB · commit 42399927）→ daily-memories/2026-10-13.md；结论：10 节自包含 HTML（数据/算力/超参/占卡/空窗期 5 试验）, DP16 推荐, GBS=1024/LR=1e-3 不变, .29 拓扑实测 NV18+RoCE 400Gb/s。需要时再读。**
  > 📦 **[已归档] #386 流水（2026-10-13 ~14:19, P-8 AdamW 监控·step4660 · loss 新低 2.646 首破 2.65）→ daily-memories/2026-10-13.md；结论：step4660/10490 loss=2.646 stable健康, grad_norm 0.117-0.198, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@4196 ✅。需要时再读。**
  > 📦 **[已归档] #385 流水（2026-10-13 ~13:42, P-8 AdamW 监控·step4530 · loss 新低 2.657106）→ daily-memories/2026-10-13.md；结论：step4530/10490 loss=2.657 stable健康, ~249K tok/s, LR=1e-3 ✅, ckpt@4196 ✅。需要时再读。**
  > 📦 **[已归档] #384 流水（2026-10-13 ~13:05, P-8 AdamW 监控·step4400 · stable 段健康推进 loss 持续下降 ✅ 新低 2.668775@step4360）→ daily-memories/2026-10-13.md；结论：step4400/10490 loss=2.670 stable健康, grad_norm 0.119-0.332, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@4196 ✅。需要时再读。**
  > 📦 **[已归档] #383 流水（2026-10-13 ~12:30, P-8 AdamW 监控·step4270 · stable 段健康推进 loss 持续下降 ✅ 新低 2.6739@step4190）→ daily-memories/2026-10-13.md；结论：step4270/10490 loss=2.679 stable健康, grad_norm 0.119-0.214, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@4196 ✅。需要时再读。**
  > 📦 **[已归档] #382 流水（2026-10-13 ~11:55, P-8 AdamW 监控·step4150 · stable 段健康推进 loss 已破 2.68 ✅ 新低 2.6756@step4130）→ daily-memories/2026-10-13.md；结论：step4150/10490 loss=2.684 stable健康, grad_norm 0.13-0.21, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@3147 ✅。需要时再读。**
  > 📦 **[已归档] #381 流水（2026-10-13 ~11:19, P-8 AdamW 监控·step4020 · stable 段健康推进 loss 已破 2.70 ✅ 新低 2.6914@step3970）→ daily-memories/2026-10-13.md；结论：step4020/10490 loss=2.696 stable健康, grad_norm 0.13-0.19, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@3147 ✅。需要时再读。**
  > 📦 **[已归档] #379 流水（2026-10-13 ~10:08, P-8 AdamW 监控·step3770 · stable 段健康推进 loss 已破 2.72 ✅ 新低 2.7142@step3710）→ daily-memories/2026-10-13.md；结论：step3770/10490 loss=2.724 stable健康, grad_norm 0.13-0.21, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@3147 ✅。需要时再读。**
  > 📦 **[已归档] #378 流水（2026-10-13 ~09:27, P-8 AdamW 监控·step3620 · stable 段健康推进 loss 已破 2.73 ✅）→ daily-memories/2026-10-13.md；结论：step3620/10490 loss=2.728 stable健康, grad_norm 0.136-0.203, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@3147 ✅。需要时再读。**
  > 📦 **[已归档] #377 流水（2026-10-13 ~08:50, P-8 AdamW 监控·step3490 · stable 段健康推进 loss 已破 2.74 ✅）→ daily-memories/2026-10-13.md；结论：step3490/10490 loss=2.735 stable健康, grad_norm 0.140-0.236, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@3147 ✅。需要时再读。**
  > 📦 **[已归档] #376 流水（2026-10-13 ~08:14, P-8 AdamW 监控·step3360 · stable 段健康推进 loss 已破 2.76 ✅）→ daily-memories/2026-10-13.md；结论：step3360/10490 loss=2.758 stable健康, grad_norm 0.135-0.215, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@3147 ✅。需要时再读。**
  > 📦 **[已归档] #375 流水（2026-10-13 ~07:37, P-8 AdamW 监控·step3230 · stable 段健康推进 loss 已破 2.78 ✅ · ckpt@3147 新保存）→ daily-memories/2026-10-13.md；结论：step3230/10490 loss=2.769 stable健康, grad_norm 0.135-0.236, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@3147 ✅。需要时再读。**
> 📦 **[已归档] #374 流水（2026-10-13 ~07:03, P-8 AdamW 监控·step3100 · stable 段健康推进 loss 已破 2.8 ✅）→ daily-memories/2026-10-13.md；结论：step3100/10490 loss=2.782 stable健康, grad_norm 0.134-0.215, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@1049+2098, next@3147。需要时再读。**
> 📦 **[已归档] #373 流水（2026-10-13 ~06:25, P-8 AdamW 监控·step2970 · stable 段健康推进 loss 持续低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step2970/10490 loss=2.803 stable健康, grad_norm 0.134-0.192, 0 NaN, ~249K tok/s, LR=1e-3 ✅, ckpt@1049+2098, next@3147。需要时再读。**
> 📦 **[已归档] #372 流水（2026-10-13 ~05:50, P-8 AdamW 监控·step2840 · stable 段健康推进 loss 持续低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step2840/10490 loss=2.802 stable健康低于3.0, grad_norm 0.127-0.201 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049+2098 均已保存 4.2GB, next@3147。需要时再读。**
> 📦 **[已归档] #371 流水（2026-10-13 ~05:15, P-8 AdamW 监控·step2720 · stable 段健康推进 loss 持续低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step2720/10490 loss=2.828 stable健康低于3.0, grad_norm 0.150-0.193 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049+2098 均已保存 4.2GB, next@3147。需要时再读。**
> 📦 **[已归档] #370 流水（2026-10-13 ~04:40, P-8 AdamW 监控·step2600 · stable 段健康推进 loss 持续低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step2600/10490 loss=2.846 stable健康低于3.0, grad_norm 0.135-0.253 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049+2098 均已保存 4.2GB, next@3147。需要时再读。**
> 📦 **[已归档] #368 流水（2026-10-13 ~03:25, P-8 AdamW 监控·step2330 · stable 段健康推进 loss 持续低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step2330/10490 loss=2.884 stable健康低于3.0, grad_norm 0.156-0.262 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049+2098 均已保存 4.2GB, next@3147。需要时再读。**
> 📦 **[已归档] #367 流水（2026-10-13 ~02:49, P-8 AdamW 监控·step2210 · stable 段健康推进 loss 持续低于 3.0 ✅ ckpt@2098 已确认保存 ✅）→ daily-memories/2026-10-13.md；结论：step2210/10490 loss=2.904 stable健康低于3.0, grad_norm 0.159-0.262 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049+2098 均已保存 4.2GB, next@3147。需要时再读。**
> 📦 **[已归档] #366 流水（2026-10-13 ~02:15, P-8 AdamW 监控·step2080 · stable 段健康推进 loss 持续低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step2080/10490 loss=2.931 stable健康低于3.0, grad_norm 0.148-0.262 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存, next@2098 即将保存。需要时再读。**
> 📦 **[已归档] #365 流水（2026-10-13 ~01:40, P-8 AdamW 监控·step1960 · stable 段健康推进 loss 持续低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step1960/10490 loss=2.952 stable健康低于3.0, grad_norm 0.154-0.208 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #364 流水（2026-10-13 ~01:06, P-8 AdamW 监控·step1840 · stable 段健康推进 loss 稳定低于 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step1840/10490 loss=2.972 stable健康低于3.0, grad_norm 0.160-0.256 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #363 流水（2026-10-13 ~00:35, P-8 AdamW 监控·step1720 · stable 段健康推进 loss 跌破 3.0 ✅）→ daily-memories/2026-10-13.md；结论：step1720/10490 loss=2.997 跌破3.0 stable健康, grad_norm 0.153-0.245 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #362 流水（2026-10-12 ~23:59, P-8 AdamW 监控·step1600 · stable 段健康推进 loss 持续下降 ✅）→ daily-memories/2026-10-12.md；结论：step1600/10490 loss=3.047 stable 段健康下降, grad_norm 0.163-0.230 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #361 流水（2026-10-12 ~23:21, P-8 AdamW 监控·step1470 · stable 段健康推进 loss 持续下降 ✅）→ daily-memories/2026-10-12.md；结论：step1470/10490 loss=3.076 stable 段健康下降, grad_norm 0.172-0.248 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #360 流水（2026-10-12 ~22:48, P-8 AdamW 监控·step1350 · stable 段健康推进 loss 持续下降 ✅）→ daily-memories/2026-10-12.md；结论：step1350/10490 loss=3.123 stable 段健康下降, grad_norm 0.164-0.286 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #359 流水（2026-10-12 ~22:11, P-8 AdamW 监控·step1220 · stable 段健康推进 loss 持续下降 ✅）→ daily-memories/2026-10-12.md；结论：step1220/10490 loss=3.164 stable 段健康下降, grad_norm 0.194-0.310 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #358 流水（2026-10-12 ~21:38, P-8 AdamW 监控·step1100 · stable 段健康推进 + 首个 ckpt@1049 已保存 ✅）→ daily-memories/2026-10-12.md；结论：step1100/10490 loss=3.228 stable 段健康下降, grad_norm 0.207-0.255 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅, ckpt@1049 4.2GB 已保存。需要时再读。**
> 📦 **[已归档] #357 流水（2026-10-12 ~21:05, P-8 AdamW 监控·step980 · stable 段健康推进 loss 持续下降 ✅）→ daily-memories/2026-10-12.md；结论：step980/10490 loss=3.296 stable 段健康下降, grad_norm 0.19-0.39 稳定, 0 NaN, ~249K tok/s, LR=1e-3 恒定 ✅。需要时再读。**
> 📦 **[已归档] #356 流水（2026-10-12 ~20:29, P-8 AdamW 监控·step860 · stable 段健康推进 loss 持续下降 ✅）→ daily-memories/2026-10-12.md；结论：step860/10490 loss=3.404 stable 段健康下降, grad_norm 0.22-0.31 稳定, 0 NaN, ~250K tok/s, LR=1e-3 恒定 ✅。需要时再读。**
> 📦 **[已归档] #355 流水（2026-10-12 ~19:55, P-8 AdamW 监控·step730 · stable 段健康推进 loss 持续下降 ✅）→ daily-memories/2026-10-12.md；结论：step730/10490 loss=3.526 stable 段健康下降, grad_norm 0.22-0.42 稳定, 0 NaN, ~250K tok/s, LR=1e-3 恒定 ✅。需要时再读。**
> 📦 **[已归档] #354 流水（2026-10-12 ~19:21, P-8 AdamW 监控·step610 · warmup 完成→stable 段健康推进 ✅）→ daily-memories/2026-10-12.md；结论：step610/10490 loss=3.734 stable 段健康下降, grad_norm 0.34 稳定, 0 NaN, ~250K tok/s, LR=1e-3 恒定 ✅。需要时再读。**
> 📦 **[已归档] #353 流水（2026-10-12 ~18:45, P-8 AdamW 监控·step490 · warmup 93.5% 健康推进 ✅）→ daily-memories/2026-10-12.md；结论：step490/10490 loss=4.16 平滑下降无spike, grad_norm 0.39 稳定, 0 NaN, ~250K tok/s, LR=9.35e-4 warmup正确。需要时再读。**
> 📦 **[已归档] #352 流水（2026-10-12 ~18:15, P-8 AdamW 监控·step370 · warmup 健康推进 ✅）→ daily-memories/2026-10-12.md；结论：step370/10490 loss=4.87 平滑下降无spike, grad_norm 0.37-0.98 稳定, 0 NaN, ~250K tok/s, LR=7.06e-4 warmup正确。需要时再读。**
> 📦 **[已归档] #351 流水（2026-10-12 ~17:40, P-8 AdamW 监控·step250 · warmup 健康推进 ✅）→ daily-memories/2026-10-12.md；结论：step250/10490 loss=5.67 平滑下降无spike, grad_norm 0.44-2.8 稳定, 0 NaN, ~250K tok/s, LR=4.77e-4 warmup正确。需要时再读。**
> 📦 **[已归档] #349 流水（2026-10-12 ~16:28, 🛑 停 dist_muon + 🟢 AdamW 从零重启 · 用户直令执行）→ daily-memories/2026-10-12.md；结论：dist_muon 停(PID1799555 SIGTERM), AdamW 新 run 启动(PID771288, from scratch, optimizer=adam, warmup524, LR1e-3)。需要时再读。**
> 📦 **[已归档] #348 流水（2026-10-12 ~15:15, P-8 监控·step8490 · 🔴 loss 慢速上漂 + grad_norm 升级 → 用户令停训换 AdamW）→ daily-memories/2026-10-12.md；结论：dist_muon step8490 loss=2.623 新高/grad_norm 0.89 → 用户令停训换 AdamW 从零重启。需要时再读。**
> 📦 **[已归档] #299~#347 流水（2026-10-11 ~ 2026-10-12, 共 ~49 条, dist_muon era 监控）→ daily-memories/2026-10-11.md / 2026-10-12.md；结论：dist_muon stable 段 step3250~8370 loss 2.596→2.437→2.623(发散), ~240-251K tok/s, ckpt@3147→4196→5245→6294→7343, 最终 step8490 loss=2.623 发散→用户令停训换 AdamW。需要时再读各日文件。**

> 📦 **[已归档] #102~#298 流水（2026-10-05 ~ 2026-10-11, 共 ~197 条）→ daily-memories/2026-10-05.md ~ 2026-10-11.md 各日文件；结论均已归档。需要时再读各日文件。**

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
- seq_length=**4094**（固定口径，非 4096）；改 seq 必须同时改 provider（recipe 已穿透）。
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
