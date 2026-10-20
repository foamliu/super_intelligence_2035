# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🚀 **【ArmD-R2 TRAINING RUNNING · step 38820/63400 (61.2%) · 2026-10-20 23:40 · wake #191】LR 轴回退至 ArmC 档（1e-3/1e-5），数据不变（6 源 14,589 shards / 173M pairs / steps 63,400）**
> **口径声明**：**LR 轴已回退至 ArmC 档（1e-3 / 1e-5）**；ArmD-R2 vs ArmC 的差异**仅剩 data(3→6源) + epoch(4→3)** 两项（比上一轮四变量更干净）。LR 与 min_lr 仍同步变动，报告中不得归因单一 LR 变量。
> **T0=09:20:34**，实测吞吐**稳态 0.75 it/s**（与 ArmC/ArmB 一致）；ETA=剩余(63400−38820)/0.75≈8.6h（log ETA=9.1h）⇒ **训练完成 ~10-21 08:45**（ETA 自 #183 起稳定 0.75–0.76，#191 复核 0.75）；+②③④⑤ 全链路 T0+28h ⇒ **~10-21 13:30**。
> **step 38820 监控**：loss 0.5795 / contr 0.5605（8.35→0.56，远低于 6.5 红线✓）/ patch 0.0190 / C1~0.5709（0.0002→0.79 稳升✓，远高于 0.05 红线）/ lr 3.53e-04 / 0.75 it/s / 0 nan/inf/oom / peak 50.4GB / 8卡100%。**无发散迹象，健康**。里程碑：s1k loss4.08/C1 0.019 · s2k loss2.63/C1 0.079(warmup结束) · s8k loss0.81/C1 0.460 · s10k loss0.96(ckpt@12:54) · s11160 loss0.4305/C1 0.6684 · s16k loss0.444/C1 0.657(已超上轮 ArmD best 0.452/0.589) · s20k ckpt_20000@16:40 · s22400 loss0.2621/C1 0.7918(原全局JOINT best) · s28k spike→s28780 已恢复 · s30k ckpt_30000@20:18(keep_ckpts2 保留 20000+30000) · s31860 loss0.3161/C1 0.7482 · s34880-35460 intra-epoch 升段→s35500 回落 振荡正常 · **s37580 loss0.2512/C1 0.7935(新全局JOINT best，扫全log确认 loss&C1 双双超 s22400)** · s38820 当前 loss0.58/C1 0.57(intra-epoch 振荡正常)。**下一 ckpt s40000 ETA ~00:30 10-21**。对照：上轮 ArmD(2e-3) s15860 best 后 s16000 发散(loss→9.3)；本轮 LR 减半 **已过 s16000 发散点至 s38820(61.2%)，零发散**，轨迹更稳。
> 🔴 **发散红线**：C1<0.05 / contr>6.5 / loss 连续 1000 步不降 / nan → 立即停并报 blocker。基准：上轮 step15,860 best loss0.452/C1 0.589，本轮 LR 减半应更早达到同等水平。
> ✅ **善后已完成**：上一轮 7 个发散产物全移入 `armD_20261019_DIVERGED_archive/`（不删除）；新目录 `armD_r2_20261020_*` 为空起步。✅ r2 全链路脚本已建（train/protb/stage1-15-2/12bench/full_chain + run_lmms_eval_r2.py，路径全 r2）。✅ full_chain watcher 已启动 PID 4063278（PHASE0 轮询等训练退出→自动跑②③④⑤）。
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

> **本唤醒流水 [wake #191, 2026-10-20 23:40]**：📊 **ArmD-R2 监控巡检**（训练运行中，距 T0 ~14.3h，**61.2%**）。实测 step **38820/63400(61.2%)**：loss 0.5795 / contr 0.5605 / patch 0.0190 / C1~0.5709 / lr 3.53e-04 / **0.75 it/s(稳态)** / peak 50.4GB / 8卡100%(50559MiB) / t=859.5min。**红线全过**：C1 0.5709≫0.05✓ / contr 0.5605≪6.5✓ / 0 数值 nan/inf/oom✓(grep 命中1=header "InfoNCE" 文本非数值) / loss 无连续1000步不降✓。⭐ **新全局 JOINT best**：扫全 log 确认 **s37580 loss0.2512/C1 0.7935**，loss&C1 双双超原 best s22400(loss0.2621/C1 0.7918)。当前 s38820 处 intra-epoch 振荡(loss0.58/C1 0.57)，同 ArmC/ArmB 模式非发散。✅ ckpt: 20000+30000+latest 在位(keep_ckpts2)。✅ full_chain watcher PID 4063278 alive。✅ 数据快照 14589 shards 不变。✅ DIVERGED_archive 7 产物在位。📦 体积：TASK=28.6KB / MEMORY=20.3KB（均≤32KB，本轮无需归档）。ETA：训练剩余(63400−38820)/0.75≈8.6h ⇒ **训练完成~10-21 08:45**；+②③④⑤ 全链路 T0+28h ⇒ **~10-21 13:30**。下一步：等训练收尾→full_chain 自动跑②ProtB→③MLLM→④12集→⑤报告。

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
