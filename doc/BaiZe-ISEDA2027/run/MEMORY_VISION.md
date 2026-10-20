# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🚀 **【ArmD-R2 TRAINING RUNNING · step 7980/63400 (12.6%) · 2026-10-20 12:0x · wake #182】LR 轴回退至 ArmC 档（1e-3/1e-5），数据不变（6 源 14,589 shards / 173M pairs / steps 63,400）**
> **口径声明**：**LR 轴已回退至 ArmC 档（1e-3 / 1e-5）**；ArmD-R2 vs ArmC 的差异**仅剩 data(3→6源) + epoch(4→3)** 两项（比上一轮四变量更干净）。LR 与 min_lr 仍同步变动，报告中不得归因单一 LR 变量。
> **T0=09:20:34**，实测吞吐稳态 0.83-0.86 it/s（优于预期 0.75-0.78）；ETA=63,400/0.84≈21.0h ⇒ **训练完成 ~10-21 06:20**；全链路 T0+27.5~28h ⇒ **~10-21 10:00-10:30**。
> **step 7980 监控**：loss 0.80（s20=9.45→单调降✓）/ contr 0.77（8.35→0.77，远低于 6.5 红线✓）/ patch 0.030 / C1 0.463（0.0002→0.463 稳升✓，远高于 0.05 红线）/ 0 nan/inf/oom / peak 50.4GB / 8卡100% 39-45°C。**无发散迹象，健康**。里程碑：s1k loss4.08/C1 0.019 · s2k loss2.63/C1 0.079(warmup结束) · s4k loss2.63/C1 0.076(局部抖动✓) · s6k loss1.59/C1 0.212 · s8k loss0.81/C1 0.460。对照：上轮 ArmD(2e-3) s15860 best loss0.452/C1 0.589 后发散；本轮 LR 减半 s8000 已 loss0.81/C1 0.46，轨迹更稳。
> 🔴 **发散红线**：C1<0.05 / contr>6.5 / loss 连续 1000 步不降 / nan → 立即停并报 blocker。基准：上轮 step15,860 best loss0.452/C1 0.589，本轮 LR 减半应更早达到同等水平。
> ✅ **善后已完成**：上一轮 7 个发散产物全移入 `armD_20261019_DIVERGED_archive/`（不删除）；新目录 `armD_r2_20261020_*` 为空起步。✅ r2 全链路脚本已建（train/protb/stage1-15-2/12bench/full_chain + run_lmms_eval_r2.py，路径全 r2）。✅ full_chain watcher 已启动 PID 4063278（PHASE0 轮询等训练退出→自动跑②③④⑤）。
> 📌 **四阶段链**（串行）：训练→②ProtB→③MLLM(Stage-1 2500/1.5 LoRA 20000/2 3500)→④12集(离线缓存)→⑤报告 `report_vision_armD_r2_20261020_mllm_stage4_zh.html`+`EXPERIMENTS_VISION.md §14`。
>
> 📦 **ArmD 原始轮（LR 2e-3, 2026-10-19~20）已归档** → daily-memories-vision/2026-10-20.md + ARCHIVE_OPERATOR_VISION.md；**结论**：ArmD(四变量: data3→6源+epoch4→3+lr→2e-3+min_lr→2e-5) 训练至 step21820 发散(loss0.45→9.3, C1 0.589→0.0002), wake#180 停止保全 ckpt_10000, 7 产物移入 DIVERGED_archive/。**已被 ArmD-R2 承接**(LR 轴回退 1e-3/1e-5)。
>
> **本唤醒流水 [wake #180, 2026-10-20 07:5x]**：🔴 **ArmD 发现已停止 — 对比训练发散**。实测 loss 轨迹(/tmp/armD_openclip_train.log)：step20 loss9.43(随机)→step10000 loss0.572(C1 0.589)→**step15860 loss0.452(全局最低)**→step16000 loss1.28→step17000 loss2.26(C1 0.12)→step19000 loss6.48(C1 0.003)→**step20000 loss9.28(C1 0.0002,=随机)**→step21500 loss9.32(停滞1500步)。contr 0.53→8.35, patch 0.04→0.97。**发散确认**(#179"非坍缩"误判,彼时为发散初期)。处置：①kill训练(129169/129177/129289+)+watcher(2056098),8卡释放4MiB,harness relay未动;②checkpoint_10000.pt(loss0.57)保全+另存checkpoint_10000_GOOD_predivergence.pt;checkpoint_20000/latest=发散态作废。**未自改超参/未重启**(遵铁律),等运维裁定(见上🔴三选一)。0 nan/oom/traceback。📦 体积：TASK=29.4KB✓/MEMORY≈31.8KB(⚠️贴上限)。详见 daily-memories-vision/2026-10-20.md。

> **本唤醒流水 [wake #181, 2026-10-20 09:2x]**：🚀 **ArmD-R2 起训**（LR 1e-3/min_lr 1e-5, 数据不变 6源14,589shards/173M pairs/steps 63,400）。T0=09:20:34。①善后：上一轮 7 发散产物全移入 armD_20261019_DIVERGED_archive/（不删），原目录清空；②建 r2 全链路脚本（run_armD_r2_openclip.sh + protb/stage1-15-2/12bench/full_chain + run_lmms_eval_r2.py，路径全 r2，sed 从 armD_20261019→armD_r2_20261020）；③自检全过（snapshot 14,589✓ / 8卡0MiB✓ / 新目录空✓）；④起训 setsid PID 3768697→torchrun PID 3768938；⑤full_chain watcher PID 4063278 已启动。首 180 步健康：loss 9.45→7.48(降✓) contr 8.35→7.01(降✓,warmup中) patch 1.10→0.47(降✓) C1 0.0002→0.0009(升✓) 0 nan/oom peak 50.4GB 8卡100% 0.57it/s(ramping)。ETA 63,400/0.77≈22.8h→训练~10-21 08:15, 全链路~10-21 12:30。口径：LR轴回退ArmC档, ArmD-R2 vs ArmC差异仅剩data+epoch。📦 体积：TASK=28.6KB✓/MEMORY=28.2KB✓(归档ArmD立案块+#177/#179流水→pointer)。详见 daily-memories-vision/2026-10-20.md。

> **本唤醒流水 [wake #182, 2026-10-20 12:0x]**：📊 **ArmD-R2 监控巡检**（训练运行中，距 T0 ~160min）。实测 step 7980/63400(12.6%)：loss 0.80 / contr 0.77 / patch 0.030 / C1 0.463 / lr 9.77e-04 / 0.84 it/s / peak 50.4GB / 8卡100% 39-45°C。**红线全过**：C1 0.463≫0.05✓ / contr 0.77≪6.5✓ / loss 降✓ / 0 nan/inf/oom✓。进程：train PID 3768938(torchrun)+8 workers 存活(etimes 9624s) / watcher PID 4063278 存活(ppid=1, 最近 11:59:38 轮询"Training still running") / full_chain log 正常。数据快照 14,589 shards✓。OUT 目录空(首个 ckpt @ step 10000, ~40min 后)。ETA 修正：0.84 it/s→63,400/0.84≈21.0h⇒训练完成~10-21 06:20, 全链路~10-21 10:00-10:30。与上轮 ArmD(2e-3)对比：上轮 s15860 best loss0.452/C1 0.589 后 s16000 发散；本轮 LR 减半 s8000 已 loss0.81/C1 0.46，loss 轨迹无发散迹象，s4000 局部抖动(loss 2.63 回弹)为对比训练正常 batch 抖动，s5000+ 已恢复下降。📦 体积：TASK=28.6KB✓/MEMORY=28.2KB✓（均≤32KB，无需归档）。

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
- [18:39 Oct17] **Wake #136**: 🔄 ArmB 监控 step15960/57250(27.9%)。详见 daily-memories-vision/2026-10-17.md。
- [19:5x Oct17] **Wake #137**: 🔄 ArmB 监控 step20520/57250(35.8%) + ✅ProtB eval脚本就绪(armB_protb_eval.py+sh, CPU单测3/3)。详见 daily-memories-vision/2026-10-17.md。
- [21:1x Oct17] **Wake #138**: 🔄 **ArmB 训练监控** — git pull fast-forward(1 commit, personal-watch), 无新运维指令。✅ ArmB 4-epoch 训练健康: step **23680/57250(41.4%)**, loss=0.27(contr=0.245 patch=0.023), C1~0.78, lr=6.99e-4, **0.85 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=462min(7.7h)。ETA (57250−23680)/0.85≈**11.0h→~08:00 10-18**。📦 体积：TASK=26.9KB / MEMORY=30.3KB。
- [22:26 Oct17] **Wake #139**: 🔄 **ArmB 训练监控** — git pull up to date，无新运维指令。✅ ArmB 4-epoch 训练健康: step **27540/57250(48.1%)**, loss=0.32(contr=0.30 patch=0.022), C1~0.74(正常振荡 0.69–0.85), lr=6.03e-4, **0.86 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=533min(8.9h)。✅ checkpoint_10000+20000+latest+open_clip_state_dict(598MB)+predictor(4.7MB)+config.json 均在。ETA (57250−27540)/0.86≈**9.6h→~08:00 10-18**; +ProtB 1–2h⇒**~09:00–10:00 10-18**。下一步: 监控→训完`run_armB_protb_eval.sh`→报告。📦 体积：TASK=26.9KB / MEMORY=30.2KB（均<32KB）。
- [06:5x Oct18] **Wake #145**: 🔄 ArmB 监控 step 53740/57250(93.9%), 0.86 it/s, ckpt@50000, 0 error。已归档 → daily-memories-vision/2026-10-18.md。
- [11:2x Oct18] **Wake #148**: ✅ **Stage-1 ArmB 训完 + Stage-1.5 ArmB 启动** — Stage-1 DONE(2500步/6.7min, final loss4.5765, proj768→2560 8.52M)；Stage-1.5 启动(20000步, LoRA r=64+proj, ETA~12:48)。详见 daily-memories-vision/2026-10-18.md。
- [15:12 Oct18] **Wake #151**: ✅ **Stage-2 DONE + lmms-eval 切 ArmB768 塔 + 12集全量启动** — Stage-2 DONE(15.3min exit0 @14:10:09 final loss1.4779, ckpt `mllm_stage2_armB/step3500/`)。代码改动：`lmms_eval_baize_llava.py` 加 `vision_backend` 开关(armB→`create_baize_vitb16_768` 768d / baize_4ep→原512d)；`run_lmms_eval.py` 加 `--vision_backend/--ckpt/--stage2_base`(ArmB 独立结果目录 `mllm_eval_results_armB/`)；新增 `launch_12benchmarks_armB.sh`；`consolidate_12benchmarks.py` 加 `--results_dir`。✅ ai2d --limit5 冒烟 PASSED(768塔 strict load/LoRA merge/生成单字母答案/exact_match=0.40/img_feat 无NaN)。🔄 12集全量 @15:12:33 启动(8 GPU, batch32, 无limit, log→`/tmp/launch_12b_armB.log`, 结果→`mllm_eval_results_armB/`)。⚠️**mmmu_pro 首跑 exit=1**(MMMU-Pro 数据集未缓存+offline→ConnectionError；其余7集OK：mmmu_val exit0/realworldqa 0.4549 等)。**mmmu_pro 已用 online 模式重跑**(GPU1, PID613521, `HF_HUB_DOWNLOAD_TIMEOUT=120` 解 10s 读超时, 输出覆写 `eval_mmmu_pro.json`)。docvqa(GPU2)仍在跑。**下一唤醒务必：等 docvqa+mmmu_pro 都完成后重新 `consolidate_12benchmarks.py --results_dir mllm_eval_results_armB`**（主 launch 的 consolidate 时 mmmu_pro 可能仍缺）。ETA~3-5h。📦 体积：TASK=31.7KB / MEMORY≈31.2KB（均≤32KB）。
- [16:38–17:05 Oct18] **Wake #152**: ✅ **12集评测DONE + 报告** — 12集首跑FAILED(15:12→15:21, 只所4集, 根因=nas_env缓存缺MMStar/MME/blink/CountBench/MMMU_Pro+offline→整组GPU崩溃)。FIX: 改指/tmp缓存(全12集预缓存), 补跑8集16:38→16:42 exit=0。ArmB平均=26.10%, ␖=25.68%, Δ=+0.42pp。**裁定: 不可分辨(边界值)**。产物: report_vision_armB_mllm_stage4_zh.html + EXPERIMENTS_VISION.md§12。详见 daily-memories-vision/2026-10-18.md。
- [18:0x Oct18] **Wake #153**: 🚀 **ArmC 训练启动** — 用户直令「开启 ArmC」+追加「wd 0.1→0.01」⇒ ArmC=两变量(min_lr 1e-4→1e-5 + wd 0.1→0.01)。✅run_armC_openclip.sh(复制 ArmB, 仅改 OUT=armC_20261018_*/min_lr 1e-5/wd 0.01, .py 复用 armB_aimv2_openclip.py)；✅run_armC_protb_eval.sh 已备(ckpt→ArmC dir)。✅.12 8卡全空(4MiB/0%)→setsid 起 ArmC 训练：8 DDP worker, log 判据行 `lr=0.001 warmup=2000 cos->min_lr=1e-05 steps=57250 wd=0.01` ✓, step60/57250 loss 8.99↓ 0.73it/s 爬坡, 8卡100%@50.5GB peak50.3GB 无OOM/无error, LPT 0.0% imbalance 11350 shards。ETA~18.4h→约 10-19 12:00。📦 体积：TASK 36208→29653B(归档 P0 ArmB→MLLM + epoch-replay 两块→ARCHIVE) / MEMORY 31166B（均≤32KB）。下一步: 监控→训完 ProtB→MLLM→12集。
- [19:31 Oct18] **Wake #154**: 🔄 ArmC 监控 step4600/57250(8.0%), 0.89it/s, log判据行确认两变量, 健康。详见 daily-memories-vision/2026-10-18.md。
- [20:52 Oct18] **Wake #155**: 🔄 ArmC 训练监控 + 体积归档 — step 8600/57250(15.0%) 健康, 0.86it/s, ckpt@10000 未到, MEMORY 33534B→21618B(归档两节运维问答→ARCHIVE)。详见 daily-memories-vision/2026-10-18.md。
- [23:27 Oct18] **Wake #157**: 🔄 ArmC 监控 step16200/57250(28.3%), 0.84it/s, ckpt@10000, 健康。详见 daily-memories-vision/2026-10-18.md。
- [22:09 Oct18] **Wake #156**: 🔄 ArmC 监控 step 12580/57250(22.0%), 0.86 it/s, ckpt@10000, 两变量确认。已归档 → daily-memories-vision/2026-10-18.md。
- [00:49 Oct19] **Wake #158**: 🔄 **ArmC 训练监控 + ③④全链路脚本就绪 + chain watcher 启动** — git fetch up to date（`## main...origin/main`，无 ahead/behind，无新运维指令；顶部 17:1x ArmC 块为最高优先，①训练已由 #153 启动）。✅ ArmC 训练健康: step **19980/57250(34.9%)**, loss~0.53(硬分片抖动非坍缩, 同 ArmB 模式), C1~0.60(正常振荡), lr=7.63e-04(cosine 下降中), **0.82 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=404min(6.7h)。✅ grep error/nan/oom/traceback=**0**；✅ ckpt@10000 已存(21:22), ckpt@20000 即将出现(~step20000)；✅ ArmB OUT dir 未被触碰。**本轮关键产出（CPU 工作, 不占 GPU）**：为 ArmC ③④阶段新建全部脚本——①`stage1_train_armC.py`/`stage15_train_armC.py`/`stage2_train_armC.py`(cp+sed from ArmB, 仅改 CKPT→armC_20261018 + OUTPUT_DIR→*_armC_20261018, 超参/数据/步数/LoRA 全不变)；②`launch_12benchmarks_armC.sh`(--vision_backend armC, LOG_DIR→mllm_eval_results_armC_20261018)；③`run_lmms_eval.py`+`lmms_eval_baize_llava.py` 已加 `armC` backend（同 armB 架构, `if vision_backend in ("armB","armC")`, 复用 create_baize_vitb16_768）；④`run_armC_full_chain.sh`(轮询训练进程退出→验证ckpt→②ProtB→③Stage1/1.5/2→④12集, 严格串行, 每步 error-check+exit on fail, 避免GPU空闲)。✅全部语法检查通过(ast.parse+bash -n)。✅**chain watcher 已在 .12 启动**(PID 4131476, /tmp/armC_full_chain.log): PHASE 0 轮询中(5min间隔), 训练退出后自动起②→③→④。ETA (57250−19980)/0.82≈**12.6h→~10-19 13:30训完**；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒**~10-19 18:00全链路完成**。下一步: chain自动跑→下一唤醒检查②ProtB结果→③④自动完成→生成报告。📦 体积：TASK=29.7KB / MEMORY=26.2KB（均≤32KB✓，无需归档）。
- [07:13 Oct19] **Wake #162**: 🔄 ArmC 监控 step37380/57250(65.3%), 0.79it/s, ckpt@20000/30000, 健康。详见 daily-memories-vision/2026-10-19.md。
- [08:37 Oct19] **Wake #163**: 🔄 ArmC 训练监控 step41020/57250(71.6%) + chain 路径核验（③④四脚本均存在），健康。详见 daily-memories-vision/2026-10-19.md。
- [09:58 Oct19] **Wake #164**: 🔄 ArmC 监控 step44920/57250(78.4%), 0.79it/s, ckpt@30000/40000, log判据行确认两变量, 健康。详见 daily-memories-vision/2026-10-19.md。
- [12:37 Oct19] **Wake #166**: 🔄 ArmC 监控 90.9% step 52060/57250, 0.78 it/s, config.json 确认两变量。已归档 → daily-memories-vision/2026-10-19.md。
- [11:1x Oct19] **Wake #165**: 🔄 ArmC 训练监控（健康，84.7%）step 48500/57250, 0.78 it/s, ETA ~14:15 训完。详见 `daily-memories-vision/2026-10-19.md`。
- [13:58 Oct19] **Wake #167**: 🔄 ArmC 训练监控（健康，97.2%，临近训完）step 55640/57250, 0.78 it/s, ETA ~14:32 训完。详见 wake#168 归档条目。
- [15:18 Oct19] **Wake #168**: 🎉 ArmC ①训练 DONE(57250步,14:32) + ②ProtB DONE(lp=62.332/5-NN=54.718) + ③MLLM 进行中。详见 daily-memories-vision/2026-10-19.md。
- [16:31 Oct19] **Wake #169**: 🔄 ArmC ③ Stage-1.5 进行中 + ④ 工具链预检就绪。详见 daily-memories-vision/2026-10-19.md。
- [18:06 Oct19] **Wake #171**: 🔄 ArmC ④ 12集 8/12 MISSING(代理宕机) → 部署代理轮询 watcher。详见 daily-memories-vision/2026-10-19.md。
- [19:36 Oct19] **Wake #172**: ✅ **ArmC ④ 12集离线缓存重跑 → 全链路 DONE** — git pull up to date，无新运维指令（顶部 17:1x ArmC 块最高优先）。✅ **根因再定位**：ArmC launch 缓存指 nas_env(缺8集) vs ArmB 成功用 `/tmp/lmms_eval_hf_datasets_app.e0031982/`(含全12集, lock 10-18 16:38)⇒**非代理问题, 是缓存路径配错**。✅ **修复**：kill 代理轮询 watcher(1153787) → 新建 `rerun_failed_benchmarks_armC_offline.sh` 把 `HF_DATASETS_CACHE`+`LMMS_EVAL_DATASETS_CACHE` 都指 /tmp、offline 无代理 → 19:42起19:46完 ALL_OK=1, `✅ All 12 benchmarks have results!`(日志确认数据集从 /tmp 缓存加载, 无 ConnectionError)。✅ **12集结果**：avg(除MME)=**25.78%** vs ArmB 26.10%, Δ=**−0.32pp**(5升6降均±2pp内), MME+101.3(不计入); DocVQA/ChartQA/OCRBench 无+10pp ⇒ **裁定不可分辨(22-26%带, 与ArmB同档)**。⚠️ 两变量(min_lr+wd)不得归因单一变量; 两变量未带来下游增益。✅ 产物: `reports/report_vision_armC_20261018_mllm_stage4_zh.html`(12KB) + EXPERIMENTS_VISION.md§13.5/§13.6/§13.7 更新为 DONE。.12 8卡全空闲。📦 体积：TASK=29.0KB / MEMORY≈30.5KB（归档#168/#169→daily-memories, 均≤32KB✓）。**ArmC 完整闭环, WAITING=1 idle 等下一运维指令**。
- [21:02 Oct19] **Wake #173**: 🔄 **idle 巡检（keep-alive，无新运维指令）** — git fetch up to date（`## main...origin/main`，无 ahead/behind；origin 最近 vision 提交=4ed5151e 19:54 wake#172 ArmC 闭环，其后均为 pretrain/zhulong/harness/data 他线提交，无新 vision 运维指令；顶部 17:1x ArmC 块仍为最高优先且已 100% 完成 ①②③④）。✅ ArmC 产物完好：`reports/report_vision_armC_20261018_mllm_stage4_zh.html`(12056B) + `vision/armC_20261018_protb_vitb16_224_results.json`(339B) + EXPERIMENTS_VISION.md§13。✅ .12 8×H100 **全空闲**（每卡 0% util / 4 MiB / 无 compute-apps）⇒ 无残留进程、无抢卡风险。✅ 工作副本未提交改动均为他线在途文件（harness/data），未触碰。距上次 vision 提交(19:54)≈68min，已过 60min 判死阈值 ⇒ 本轮 keep-alive 心跳。📦 体积：TASK=29.0KB / MEMORY=29.2KB（均≤32KB✓，无需归档）。**WAITING=1，idle 等下一运维指令**。

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- Wakes #47/#49/#50/#51（2026-10-13）已归档至 `daily-memories-vision/2026-10-13.md`（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
