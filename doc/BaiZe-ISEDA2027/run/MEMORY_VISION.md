# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🚀 **【ArmD-R2 TRAINING DONE · step 63400/63400 (100%) · exit 0 · 2026-10-21 10:02:49 · wake #199】→ Phase ② ProtB eval RUNNING（10:05:22 起，特征提取 ~70%）· full_chain watcher PID 4063278 自动串行②③④⑤**
> **口径声明**：**LR 轴已回退至 ArmC 档（1e-3 / 1e-5）**；ArmD-R2 vs ArmC 的差异**仅剩 data(3→6源) + epoch(4→3)** 两项。LR 与 min_lr 同步变动，报告中不得归因单一 LR 变量。
> **训练结果**：T0=09:20:34(10-20)→完成 10:02:49(10-21)，**总耗时 ~24.7h**，稳态 0.71–0.75 it/s。**最终 step 63400**：loss 0.6750 / contr 0.6611 / patch 0.0139 / C1~0.5163 / lr 1.00e-05（=min_lr）。⭐ **全局 JOINT best = s43700 loss0.1360 / C1 0.8902**（全 log awk 确认）。**全程 0 nan/inf/oom**（grep loss=nan/inf 命中 0）。末段硬分片抖动（s58000–63400 loss 0.14–1.07 振荡、C1 0.29–0.89），同 ArmC/ArmB 模式非发散。里程碑：s2k loss2.63/C1 0.079 → s11160 loss0.4305/C1 0.6684 → s22400 loss0.2621/C1 0.7918 → s37580 loss0.2512/C1 0.7935 → ⭐s43700 loss0.1360/C1 0.8902(best) → s58800 loss0.1427/C1 0.8807(逼近) → s63400 loss0.675/C1 0.52(末段抖动)。
> **产物**：OUT=`armD_r2_20261020_aimv2_openclip_vitb16_224/`：checkpoint_60000.pt + checkpoint_63400.pt + latest.pt(=s63400) + open_clip_state_dict.pt(599MB) + predictor.pt(4.7MB) + config.json。keep_ckpts2 保留 50000+60000(已滚动删 40000)。✅ config 复核：lr=0.001/min_lr=1e-05/wd=0.01/seed=1234/mask_ratio=0.6/contrast=1.0/patch=1.0/n_visual=86192640(86.2M) 全对。⚠️ ProtB 用 open_clip_state_dict.pt(=latest=s63400 末段抖动态，同 ArmB/ArmC 口径)；末段抖动或使 final lp 略低于 best 段——属协议已知特征。
> **ETA（全链路）**：②ProtB ~11:05(+1h) → ③MLLM 三阶段 ~13:00(+1.8h) → ④12集 ~14:30(+1.5h) → ⑤报告 ~15:00(+0.5h，**手动**，full_chain 不自动)。⇒ **全链路完成 ~10-21 15:00**。
> ✅ **善后**：上一轮 7 个发散产物全在 `armD_20261019_DIVERGED_archive/`；r2 全链路脚本就绪；full_chain watcher PID 4063278(ppid=1) 自动串行②③④。⑤报告需手动生成 `report_vision_armD_r2_20261020_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §14`。
> 📌 **四阶段链**（串行）：训练→②ProtB→③MLLM(Stage-1 2500/1.5 LoRA 20000/2 3500)→④12集(离线缓存)→⑤报告 `report_vision_armD_r2_20261020_mllm_stage4_zh.html`+`EXPERIMENTS_VISION.md §14`。
>
> 📦 **ArmD 原始轮（LR 2e-3, 2026-10-19~20）已归档** → daily-memories-vision/2026-10-20.md + ARCHIVE_OPERATOR_VISION.md；**结论**：ArmD(四变量: data3→6源+epoch4→3+lr→2e-3+min_lr→2e-5) 训练至 step21820 发散(loss0.45→9.3, C1 0.589→0.0002), wake#180 停止保全 ckpt_10000, 7 产物移入 DIVERGED_archive/。**已被 ArmD-R2 承接**(LR 轴回退 1e-3/1e-5)。
>
> 📦 **wake #180 (07:5x, ArmD 发散发现+停止保全 ckpt_10000)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #181 (09:2x, ArmD-R2 起训 T0=09:20:34 + 善后+建脚本+watcher)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #182 (12:0x, ArmD-R2 监控 step7980, 0.84 it/s 早期较快段)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #183 (13:1x, ArmD-R2 监控 step11020, ETA 修正稳态 0.78 it/s, 训练完成~10-21 08:10)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #184 (14:32, ArmD-R2 监控 step14480, s14240 新 best loss0.444/C1 0.659 超上轮)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #185 (15:56, ArmD-R2 监控 step18080, 过发散点 s16000 零发散确认)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #186 (17:12, ArmD-R2 监控 step21240, 全局best s11160 loss0.4305/C1 0.6684)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #188 (19:46, ArmD-R2 监控 step28780, 全局joint best s22400 loss0.2621/C1 0.7918 确认, s28k spike 已恢复非发散, 红线全过, 脚本复核 r2 路径/LR 全对, ETA 训练~10-21 08:25/全链路~13:15)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #189 (21:06, ArmD-R2 监控 step32000/50.5%, 稳态0.76 it/s, 红线全过, 半程零发散确认)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #190 (22:26, ArmD-R2 监控 step35500/56%, 0.75it/s, 红线全过, 全局joint best s22400 不变)** 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 **wake #192 (00:55, ArmD-R2 监控 step41820/66.0%, 红线全过, 全局best s37580 不变)** 已归档 → daily-memories-vision/2026-10-21.md。
> 📦 **wake #193 (02:10, ArmD-R2 监控 step44960/70.9%, 新全局best s43700 loss0.1360/C1 0.8902 确认, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。

> 📦 **wake #194 (03:30, ArmD-R2 监控 step49280/77.7%, 红线全过, 全局best s43700 不变)** 已归档 → daily-memories-vision/2026-10-21.md。
> 📦 **wake #195 (04:45, ArmD-R2 监控 step52440/82.7%, s50000 ckpt 落盘, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。
> **本唤醒流水 [wake #197, 2026-10-21 07:34]**：📊 **ArmD-R2 监控巡检**（训练运行中，距 T0 ~22.2h，**92.7%**）。实测 step **58780/63400(92.7%)**：loss 0.1373 / contr 0.1219 / patch 0.0154 / C1~0.8853 / lr 2.38e-05 / **0.74 it/s(稳态)** / peak 50.4GB / 8卡100%(50559MiB) / t=1332.7min(22.2h)。**红线全过**：C1 0.8853≫0.05✓ / contr 0.1219≪6.5✓ / 0 nan/inf/oom✓(全 log grep 命中0) / loss 持续下降✓。✅ **s55620 spike 完全恢复确认**：s55620 spike 峰 loss1.2427/C1 0.2933→s58780 loss0.1373/C1 0.8853（loss 降 9.0×、C1 升 3.0×，~3160 步内恢复），证实「硬分片振荡非发散」判断正确；同 ArmC/ArmB 末段模式（ArmC 末段抖动仍 lp62.332）。⭐ **全局 JOINT best 仍 s43700 loss0.1360/C1 0.8902**（全 log awk 复核，s53420 loss0.1370/C1 0.8875 与 s58780 loss0.1373/C1 0.8853 均逼近但未超）。✅ ckpt: 40000+50000+latest+open_clip_state_dict(598MB)+predictor(4.7MB)+config 在位(keep_ckpts2)。✅ full_chain watcher PID 4063278 alive(ppid=1, etimes 79787s≈22.2h, PHASE0 轮询300s, 最近[07:30:13]"Training still running") + 训练主进程 PID 3768697 alive(ppid=1, etimes 80025s) + 8 DDP rank alive。✅ 数据快照 14589 shards 不变。✅ DIVERGED_archive 7 产物在位。📦 体积：TASK=27.9KB / MEMORY=28.2KB（均≤32KB✓，本轮无需归档）。ETA：训练剩余(63400−58780)/0.74≈1.73h ⇒ **训练完成~10-21 09:18**；+②③④⑤ 全链路 T0+28h ⇒ **~10-21 13:30**。下一 ckpt s60000 ETA ~07:40（即将落盘）。下一步：等训练收尾→full_chain 自动跑②ProtB→③MLLM→④12集→⑤报告。
> **本唤醒流水 [wake #198, 2026-10-21 09:00]**：📊 **ArmD-R2 监控巡检**（训练运行中，距 T0 ~23.7h，**97.2%**，即将收尾）。实测 step **61640/63400(97.2%)**：loss 1.0701 / contr 1.0569 / patch 0.0132 / C1~0.3475 / lr 1.21e-05 / **0.72 it/s(末段略降)** / peak 50.4GB / 8卡100%(50559MiB) / t=1417.8min(23.6h)。**红线全过**：C1 0.3475≫0.05✓ / contr 1.0569≪6.5✓ / 0 nan/inf/oom✓(grep 全 log 命中0数值) / loss 连续不降非单调(振荡含频繁下探 s60800 0.37/s61300 0.88/s61580↘)✓。⚠️ **末段硬分片抖动(非发散)**：s61060 loss0.61→s61640 loss1.07(C1 0.55→0.35)，但全程高频振荡含下探，同 ArmC/ArmB「末段硬分片抖动」(ArmC 末段抖动仍 lp62.332)；与上轮 ArmD(2e-3) 发散(loss→9.3/C1→0.0002)本质不同。⭐ **全局 JOINT best 仍 s43700 loss0.1360/C1 0.8902**（全 log awk 复核，本轮未刷新）。✅ **s60000 ckpt@08:04 已落盘**(checkpoint_60000.pt 1.81GB + latest.pt + open_clip_state_dict.pt 599MB + predictor.pt 4.7MB + config.json；keep_ckpts2 现保留 50000+60000；40000 已滚动删)。✅ full_chain watcher PID 4063278 alive(ppid=1, etimes 84887s≈23.6h, PHASE0 轮询300s, 最近[09:00:18]"Training still running") + 训练主进程 PID 3768697 alive(ppid=1, etimes 85125s) + 8 DDP rank alive(ps 确认 --output-dir armD_r2_20261020_* --lr 1e-3 --min-lr 1e-5 --steps 63400 --keep-ckpts 2 全对)。✅ 数据快照 14589 shards 不变。✅ DIVERGED_archive 7 产物在位。⚠️ **报告须注明**：latest.pt(=step63400)将处末段抖动态，ProtB 用 latest.pt(同 ArmB/ArmC 口径)；全局 best s43700 未单独存 ckpt(keep_ckpts2 仅留 50000+60000)，末段抖动或使 final lp 略低于 best 段——属协议已知特征。📦 体积：TASK=28.6KB / MEMORY=30.3KB（均≤32KB✓，本轮无需归档）。ETA：训练剩余(63400−61640)/0.72≈0.7h ⇒ **训练完成~10-21 09:42**；+②ProtB 1h+③MLLM 1.8h+④12集 1.5h+⑤报告 0.5h ⇒ **全链路~10-21 14:00**。下一步：等训练收尾(~42min)→full_chain watcher 自动检测训练退出→跑②ProtB→③MLLM→④12集→⑤报告；下一唤醒查②ProtB 结果(lp/5-NN 对比 ArmB 62.093/58.102、ArmC 62.332/54.718)+③④进度。
> **本唤醒流水 [wake #199, 2026-10-21 10:31]**：🎉 **ArmD-R2 训练完成 → Phase ② ProtB eval 运行中**。✅ 训练 **DONE**：step 63400/63400(100%)，exit 0，完成于 **10:02:49**（T0=09:20:34 10-20，总耗时 ~24.7h，稳态 0.71–0.75 it/s）。最终 loss 0.6750 / C1~0.5163 / lr=1.00e-05(=min_lr)；⭐全局 best **s43700 loss0.1360/C1 0.8902**；**全程 0 nan/inf/oom**（grep loss=nan/inf 命中 0；96 条 grep 命中全为 NFS silly-rename traceback 中 `sys.exc_info()` 文本，非数值异常）。✅ 产物：checkpoint_60000.pt + checkpoint_63400.pt + latest.pt + open_clip_state_dict.pt(599MB) + predictor.pt(4.7MB) + config.json；config 复核 lr=0.001/min_lr=1e-05/wd=0.01/seed=1234/mask_ratio=0.6/contrast=1.0/patch=1.0/n_visual=86192640(86.2M) **全对**。🔄 **Phase ② ProtB eval RUNNING**（full_chain watcher PID 4063278 于 10:05:22 检测训练退出→自动启动 `run_armD_r2_protb_eval.sh` PID 3729177）：8 并行 shard 跨 8 卡(cuda:0–7, 各 3257MiB)，val 特征提取 DONE(50000 imgs→[50000,512])，probe-train 特征提取 ~70%（各 shard ~26/37 parquet files）；线性探针(SGD 90ep×3seeds)待特征提取完成后启动。⚠️ 日志行前缀 `[ArmB]`=py 脚本 logger 名硬编码，实为 ArmD-R2 run。📦 **体积维护**：归档 wake #191–#195(5 条全文)→daily-memories-vision/2026-10-21.md，MEMORY 从 32505B→**26344B**（≤32KB✓）。ETA：②ProtB ~11:05(+1h) → ③MLLM ~13:00(+1.8h) → ④12集 ~14:30(+1.5h) → ⑤报告 ~15:00(**手动**)。下一步：下一唤醒查②ProtB 结果(lp/5-NN 对比 ArmB 62.093/58.102、ArmC 62.332/54.718)+③④进度→全链路完成后手动生成报告。


> **本唤醒流水 [wake #196, 2026-10-21 06:06]**：📊 **ArmD-R2 监控巡检**（训练运行中，距 T0 ~20.8h，**87.9%**）。实测 step **55620/63400(87.9%)**：loss 1.2427 / contr 1.2265 / patch 0.0162 / C1~0.2933 / lr 4.87e-05 / **0.74 it/s(稳态)** / peak 50.4GB / 8卡100%(50559MiB, GPU7 util 采样0%瞬态) / t=1245.8min(20.8h)。**红线全过**：C1 0.2933≫0.05✓ / contr 1.2265≪6.5✓ / 0 nan/inf/oom✓(全 log 3044 行 grep loss=nan/inf 命中0) / loss 连续不降步数 620<1000✓。⚠️ **当前处硬分片振荡 spike 峰段(非发散)**：s55000 loss0.3155/C1 0.7423(局部谷)→s55620 loss1.2427/C1 0.2933 单调升 620 步，但**增量递减**(s55540→55620: +0.106/+0.082/+0.066/+0.036)显减速接近峰转。epoch-3 共 4 次同类 spike(s50120 0.89/s51680 0.86/s54540 1.01/s55580 1.14)**均 ~500-1000 步内恢复**至 loss0.2/C1 0.8（envelope 扫描 s50120→s55620 每 250 步确认）。同 ArmC/ArmB「末段硬分片抖动」模式（ArmC 末段抖动0.077-0.203 仍得 lp62.332，因 spike 为 batch 组成效应非权重退化）；与上轮 ArmD(2e-3) 发散(loss0.45→9.3/C1 0.589→0.0002)本质不同。⭐ **全局 JOINT best 仍 s43700 loss0.1360/C1 0.8902**（全 log awk 复核，本轮未刷新）。✅ ckpt: 40000+50000+latest+open_clip_state_dict(598MB,当前映 s50000)+predictor(4.7MB)+config 在位(keep_ckpts2)。✅ full_chain watcher PID 4063278 alive(ppid=1, etimes 74512s≈20.7h, PHASE0 轮询300s, 最近[06:05:09]"Training still running") + 训练主进程 PID 3768697 alive + 8 DDP rank alive(ps 确认 --output-dir armD_r2_20261020_* --lr 1e-3 --min-lr 1e-5 --steps 63400 --keep-ckpts 2 全对)。✅ eval 链复核: run_armD_r2_protb_eval.sh 用 open_clip_state_dict.pt(最终权重, 同 ArmB/ArmC 先例—ArmC 末段振荡仍 lp62.332), full_chain ②→③→④ 自动串行已就绪。✅ 数据快照 14589 shards 不变。✅ DIVERGED_archive 7 产物在位。📦 体积：TASK=27.9KB / MEMORY=26.3KB（均≤32KB✓，本轮无需归档）。ETA：训练剩余(63400−55620)/0.74≈2.9h ⇒ **训练完成~10-21 09:00**；+②③④⑤ 全链路 T0+28h ⇒ **~10-21 13:30**。下一 ckpt s60000 ETA ~07:35。下一步：等训练收尾→full_chain 自动跑②ProtB→③MLLM→④12集→⑤报告；若最终 open_clip_state_dict 落在 spike 谷, 可用 ckpt_50000/60000 做 ProtB 对照(待运维定)。




> 📦 **wake #191 (23:40, ArmD-R2 监控 step38820/61.2%, 新全局joint best s37580 loss0.2512/C1 0.7935, 红线全过)** 已归档 → daily-memories-vision/2026-10-21.md。

> 📦 wake #187 (18:28, ArmD-R2 监控 step24560, 全局best C1 0.7918@s22400 超原best) 已归档 → daily-memories-vision/2026-10-20.md。


> 📦 wake #179 (06:2x, ArmD 监控 keep-alive) 已归档 → daily-memories-vision/2026-10-20.md。

> 📦 wake #177 (03:5x, ArmD 监控 keep-alive) 已归档 → daily-memories-vision/2026-10-20.md。

> ✅ **ArmC 全链路 DONE（wake #172, 2026-10-19 19:46）** — 详见 `run/reports/report_vision_armC_20261018_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §13` + `ARCHIVE_OPERATOR_VISION.md`。要点：**两变量**（min_lr 1e-4→1e-5 + wd 0.1→0.01）；①训练 57,250 步 ✓ ②ProtB lp 62.332±0.014 / 5-NN 54.718（vs ArmB 62.093/58.102）③MLLM 三阶段 ✓ ④**12/12 DONE，avg(除 MME) 25.78% vs ArmB 26.10% = Δ−0.32pp，裁定不可分辨**；逐集 Δ 全在 ±2pp 内（5 升 6 降）。⏭ **已被 ArmD 承接**（见上）。
 > 📦 ArmB 全程（2026-10-17 09:1x ~ 10-18 07:55，wake #128~#145）+ 10-14~16 全天流水已归档 → `daily-memories-vision/2026-10-1{7,8}.md` + `ARCHIVE_OPERATOR_VISION.md`；**结论**：ArmB 训练 57,250 步健康（0.85–0.87 it/s）、ProtB lp 62.093 / 5-NN 58.102、MLLM 12 集 26.10%、报告 `report_vision_armB_mllm_stage4_zh.html` + `§12`。需要时再读。
 > 📦 2026-10-18 15:12（wake #151 Stage-2 DONE+切ArmB768塔+12集首跑启动）已归档 → daily-memories-vision/2026-10-18.md；**结论**：Stage-2 DONE(15.3min,loss1.4779)；lmms-eval加vision_backend开关；ai2d冒烟PASS；12集首跑@15:12启动(后证实FAILED,见#152)。
 > 📦 2026-10-17 23:37（wake #140: ArmB step31480(55%)健康,ETA~07:50 10-18）已归档 → daily-memories-vision/2026-10-17.md。
> 📦 2026-10-17 21:1x~19:5x（🔄 ArmB 监控 · wake #136~#139）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step15960→27540 健康, 0.85-0.87 it/s, ckpt@20000+10000已存, P1 ArmA 报告交付, ETA~08:00 10-18。
> 📦 2026-10-17 14:5x~17:27（🔄 ArmB 监控 · wake #133~#135）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step4540→12120 健康, P1 ArmA 中文报告交付(commit 2f15f88e), 0.86 it/s 稳态, checkpoint_10000 已存。
>
> 📦 2026-10-17 13:3x（🔄 ArmB 改 4 epoch 重启 · wake #132）已归档；**结论**：4-epoch run(steps=57250)由 wake #132 启动(PID 1203148)，wake #133 确认健康运行中(step 4540)。
>
> 📦 2026-10-17 09:1x~12:4x（wake #128~#131: ArmA 训练完成154500步 + ProtB lp=58.03±0.02%/5-NN=53.98% + Stage(iv)报告闭环(da8e9cd1) + ArmB 3-epoch 启动后被 #132 改 4-epoch）已归档 → daily-memories-vision/2026-10-17.md。
>
> 📦 **改动清单 + 10-14~16 全天流水**（wake #106~#128, ArmA 起训/12集 eval/Stage-1/1.5/2/open_clip wrapper）已归档 → daily-memories-vision/2026-10-{14,15,16}.md + ARCHIVE_OPERATOR_VISION.md；**结论**：✅ ArmA 全链路完成, 改动清单(LPT/workers/cudnn/fused)已落地, 配方不变。
> ✅ **④-4ep 基线（COMPLETE）**: ProtB 67.05±0.02% / ProtA 56.70% / zs 40.64%/72.64% / k-NN 42.35%. final_loss=0.0805, C1=0.5932, 748,404 steps, 60,545s. VERDICT: MODERATE, DIMINISHING. 详见 EXPERIMENTS_VISION.md §9.5/§9.7.
> 📦 ④-2ep / V2 Muon / V3 / ② probe / ④-4ep评测（2026-10-11~13）已归档 → daily-memories-vision/2026-10-14.md + ARCHIVE_OPERATOR_VISION.md；**结论**：V2 Muon 坍缩❌；V3 不可分辨；② probe=ceiling；④-2ep MODERATE；④-4ep 67.05% 递减确认。
> ✅ **③ 参照系说明** in `EXPERIMENTS_VISION.md §8.3`: BaiZe internal protocol labeling rules, 不可比原因逐条.

| 字段 | 值 |
|:---|:---|
| PHASE | 🔄 **ArmC ④ 12集 8/12 MISSING→重跑（wake #171, .12 8卡空闲）**。ArmC=两变量(min_lr 1e-4→1e-5 + wd 0.1→0.01)。①训练✅DONE 14:32(57250步,exit0). ②ProtB✅DONE 14:57 lp=62.332/5-NN=54.718(vs ArmB 62.093/58.102 Δlp+0.239/Δ5NN−3.384, 两变量). ③MLLM✅全DONE(Stage-1 15:06/Stage-1.5 step20000/Stage-2 step3500). ④12集 chain 17:27 完成**但 8/12 MISSING**(mmmu_pro/chartqa/ocrbench/countbench/mme/blink/ai2d/mmstar)；仅 4 集成功(mmmu_val.4256/docvqa.0758/infovqa.1709/realworldqa.4497)；根因=ConnectionError 于 task.download()(launch 设 HF_HUB_OFFLINE=1+HF_DATASETS_OFFLINE=1, 17:17 代理flaky, 非模型问题). ✅.12 8卡全空闲(4MiB/0%). **本轮**: 重跑 4 失败GPU组(GPU1 mmmu_pro / GPU4 chartqa+ocrbench+countbench / GPU5 mme+blink / GPU6 ai2d+mmstar, 去offline flag)→重consolidate→generate_armC_mllm_report.py→EXPERIMENTS §13→commit. ArmB 12集全成功(26.10%). **WAITING=1**（④ 重跑中）。 || ERROR_COUNT | 20（同前） |
| BUDGET_USED | ~999 GPU·h (V3 ~106, ② ~1, ④-2ep ~80, ④-4ep ~134 incl. eval) |
| 更新 | **2026-10-19 13:58 (wake #167)**: 🔄ArmC 巡检健康(临近训完)。step **55640/57250(97.2%)**(+3580自#166, ~1.4h), loss=0.13(contr=0.11 patch=0.016, 末段硬分片抖动0.077-0.203非坍缩,同ArmB模式), C1~0.83-0.92(正常), lr=1.21e-05(cosine→min_lr=1e-5), 0.78it/s(稳态), 7/8×H100 100%@50559MiB(card1批间偶0%) peak50.4GB 无OOM, t=1192.5min(19.9h)。✅grep error/nan/oom/traceback=0；✅盘上核(OUT=/nas_train/app.e0031982/datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/) ckpt@40000(08:17)+50000(11:51)+latest+open_clip_state_dict(598MB)+predictor(4.7MB)+config.json 均在(10000/20000/30000已滚动删, keep-ckpts2), final@57250~14:32；✅**config.json复核**: lr=0.001/min_lr=1e-05/wd=0.01/seed=1234/mask_ratio=0.6/contrast_weight=1.0/patch_loss_weight=1.0/n_visual=86192640(86.2M,与ArmB一致) → **只有 min_lr+wd 两变量** ✓；✅ArmB OUT dir未被触碰(ckpt_50000/57250 10-18完好)。✅**chain watcher PID 4131476存活**(ppid=1, /tmp/armC_full_chain.log PHASE0轮询5min, 最近[13:55:08]\"Training still running\"), 训练DDP worker PID 4154295等存活。⚠️日志行前缀`[ArmB]`=py脚本logger名硬编码, 实为ArmC run, 报告须注明。ETA (57250−55640)/0.78≈0.57h→~14:32训完；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒~10-19 19:00全链路完成。下一步: chain自动跑②→③→④；下一唤醒查②ProtB结果(lp/5-NN对比ArmB 62.093/58.102、④-4ep 67.05)+③④进度→生成报告 report_vision_armC_20261018_mllm_stage4_zh.html + EXPERIMENTS_VISION.md §13。📦 体积：TASK=29.7KB / MEMORY=30.4KB（均≤32KB✓，无需归档）。 |

### 评测耗时归因（2026-10-15）

| 环节 | 耗时(估) | 说明 |
|:--|:--|:--|
| 训练链 (Stage-1/1.5/2) | ~4h | Stage-1 2500步(~1.5h) + Stage-1.5 20000步(~2h) + Stage-2 3500步(0.26h) + gate check/smoke(~0.3h) |
| adapter 适配 (lmms-eval wrapper) | ~3h | `lmms_eval_baize_llava.py` 编写+调试(generate_until/loglikelihood/multi-GPU LOCAL_RANK/batch_size) |
| 数据通道 (HF 下载) | ~1.5h | proxy 直连 hf.co；ai2d smoke 77MB OK；17 集首次下载是大头(预建缓存中) |
| 磁盘满崩溃 + 修复 | ~0.5h | limit50 8卡同时写 `/home`(47G)→崩；修复=迁 HF_HOME→/nas_env + 单进程预建缓存 |
| git 推送阻塞 | ~6h | `.12` 直连 github 不通(无 proxy)→ 6h 推不上来(运维已配 git config http.proxy=92.23 修复) |
| generate 输出 bug | ~0.5h | 早期 ai2d 输出解析调试(`HF_TOKEN=hf_dummy` + adapter 输出格式) |
> 📦 「运维问答·下一步工作建议 · 2026-10-08③」（1-A~1-D / 2-A~2-E / 3 GPU空窗 / 4-A~4-E 论文）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：旧版下一步建议（w384/336 AIMv2、C1-lp 消融、Stage-iv 前置、论文补 Limitations），多数已被后续 ArmA/ArmB/ArmC 工作覆盖（④-4ep 67.05%、V2全量=ArmB 62.09%、MLLM=ArmB 12集 26.10%）。需要时再读。
> 📦 「运维问答·下一步工作建议 · 2026-10-10」（④epoch缩放 / V2全量 / MLLM前置 / 论文 / w384 / 336 / C1-lp 排序）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：④epoch→④-4ep(67.05% MODERATE/DIMINISHING)；V2全量→ArmB(62.09%)；MLLM前置→ArmB Stage-iv 完成(12集 26.10% 不可分辨)。需要时再读。

## R9 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND9.md）

> 📦 R9 converged 结论（w512 选定 / scaling 幂律 acc=0.251−0.864·N^−0.090 渐近 25.1% / 瓶颈=数据量与目标函数非架构）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节。需要时再读。

## R10 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND10.md）

> 📦 R10 converged 结论（2D 拟合 M 边际全区间为负 / w384@15.36M=7.99% 全宽最高 / 加宽塔数据受限区间负收益）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节。需要时再读。

## R14 官方仓库调研（✅ 全部完成，2026-10-03）

> 📦 R14 官方仓库调研（OpenVision/AIMv2/OpenVision2/FastVLM/MambaEye/MoE-ViE 普查 + LICENSE + patch14/d24 vs 我们 patch16/d30）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节；产物 `VISION_OFFICIAL_REPOS_SURVEY.md`。需要时再读。

## E1 GPIC 规模实测（✅ 完成，2026-10-03）

> 📦 E1 GPIC 规模实测（12,537 对/tar → 全量≈100.3M / short 45% / C1 口径 18.5M·32M·118M 三类分母）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节。需要时再读。

## R11-L / R11-L2 / caption-weight / R11-F / R11-G / R11-H / R12 / 3-epoch 全部完成

> 📦 以上全部已闭合实验（R11-L 四臂→R11-L2→caption-weight→R11-F→R11-G→R11-H→R12→3-epoch 续跑）的详细流水已滚动归档 → `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（**原文未改**）。**结论以 `EXPERIMENTS_VISION_ROUND11.md` + `EXPERIMENTS_VISION_ROUND12.md` 为权威。**

**一句话结论**：R11-L 四臂（SigLIP/LocalLoss/CoCa/基线）**无一翻盘**；R11-L2 文本塔解冻（LoRA）**未翻盘**（−0.80 pp）；caption-weight 三点消融 → **caption 监督与 IN-1k 正交**；R11-F 数据源横比 → GPIC short/medium/short+medium **无显著差异**；⭐ **R11-G AIMv2 长跑翻盘**（lp@55.3M=19.76% vs 基线 7.40%，R²=0.91，渐近 >>25.1%）；R11-H 纯 AR **无翻盘**（翻盘依赖对比项）；R12 全量 58.8M 1.05 epoch lp@61.4M=17.57%（< R11-G 同 N）；3-epoch 续跑 344k/176M lp=20.27%，35 点 scaling R²=0.94，非单调 7/34，a 撞上界不可定。

> 📦 [04:20 Oct12] 全量 1-epoch 耗时估算 + AIMv2 提速归因实测（bs/nw 扫描）已归档 → daily-memories-vision/2026-10-12.md「Archived from MEMORY_VISION.md」节。**结论**：bs=64 下数据/IO 受限（GPU util~70%），~5000 img/s 是 NFS 架构上限；1 epoch ≈ 5.2–9.1h。需要时再读。

## 本唤醒流水

> 📦 [Oct 13~14] 本唤醒流水旧条目（Wake #45~#84, 含 ArmC 监控/MLLM bridge/报告刷新/④-4ep eval/外部编码器, ~15条）已归档 → daily-memories-vision/2026-10-{13,14}.md。**关键结论**：ArmC 154500步完成(ProtB 68.25%), ④-4ep ProtB 67.05%, MLLM bridge 5/5 PASSED, 外部编码器 SigLIP2 87.46% 最高。需要时再读。
> 📦 10-06~10-12 早期流水（R12b/scaling/fair-rerun/V3/②probe/④-2ep/④-4ep, ~40条）已归档 → daily-memories-vision/2026-10-{06..12}.md。**关键结论**：E1fair vs E2fair Δlp=+0.17pp indistinguishable; ④-4ep ProtB 67.05% MODERATE/DIMINISHING; ④-2ep ProtB 65.37%。需要时再读。
> 📦 [Oct 16] 本唤醒流水旧条目（Wake #108~#115, 含 precache 监控/Part B 验收/limit50 abort/12集 eval 完成/keepalive, 5条）已归档 → daily-memories-vision/2026-10-16.md。**关键结论**：✅ Part B 三项验收全通过(ai2d=0.60)；✅ 12/12 benchmarks 全量 eval 完成(ai2d 60.04%/mmmu 42.89%/realworldqa 43.01%)；consolidated_12benchmarks.json 交付。需要时再读。
> 📦 [Oct16 20:50~23:1x] Wake #118~#120（ArmA 监控+效率专项落地）已归档 → daily-memories-vision/2026-10-16.md；**结论**：ArmA step21940 健康；效率优化一揽子落地(修前2.40→修后3.35 it/s +40%, util 95-100%全卡, 三项验收全达标)。
> 📦 [00:30~17:27 Oct17] Wake #121~#135 内联流水（ArmA 监控 step59480→103400 + ArmA 训完154500步/ProtB 58.03% + ArmB 起训 step4540→12120 + P1 ArmA 中文报告交付, 6条）已归档 → daily-memories-vision/2026-10-17.md。**关键结论**：ArmA 3.35-3.37 it/s 稳定训完, ProtB lp 58.03±0.02%/5-NN 53.98%, ArmB 4-epoch 起(PID 1203148→1203161), 0.86-0.89 it/s, 无 OOM/无错误。需要时再读。
- 📦 **Wake #136~#152（2026-10-17~18, ArmB 训练监控/ProtB/12集）已滚动归档** → daily-memories-vision/2026-10-{17,18}.md。**结论**：ArmB 4-epoch 训完 57250 步；ProtB lp 62.093/5-NN 58.102；12集 avg 26.10%（首跑 4/12 失败因 nas_env 缓存缺集→改指 /tmp 修复），裁定不可分辨。需要时再读。
- 📦 **Wake #153~#158（2026-10-18~19, ArmC 训练启动+监控+③④脚本+chain watcher）已滚动归档** → daily-memories-vision/2026-10-{18,19}.md。**结论**：ArmC=两变量(min_lr 1e-4→1e-5 + wd 0.1→0.01)，57250 步训完；③④全链路脚本(stage1/1.5/2+12bench+full_chain)就绪，chain watcher 启动自动跑②③④。需要时再读。
- 📦 **Wake #162~#173（2026-10-19, ArmC 监控→训完→ProtB→MLLM→12集→全链路 DONE→idle keep-alive）已滚动归档** → daily-memories-vision/2026-10-19.md。**结论**：ArmC ①训练 DONE(57250步) + ②ProtB lp 62.332/5-NN 54.718 + ③MLLM 三阶段 DONE + ④12集 avg(除MME) **25.78%** vs ArmB 26.10% = Δ−0.32pp **裁定不可分辨**；根因=缓存路径配错(非代理)→改指 /tmp 修复全 12 集。两变量(min_lr+wd)未带来下游增益。ArmC 完整闭环，已被 ArmD 承接。需要时再读。

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- Wakes #47/#49/#50/#51（2026-10-13）已归档至 `daily-memories-vision/2026-10-13.md`（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
