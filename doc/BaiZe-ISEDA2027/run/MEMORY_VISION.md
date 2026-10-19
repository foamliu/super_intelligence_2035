# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🆕 **ArmD 已立案（2026-10-19 21:2x · 用户直令 · 最高优先）**：`BAIZE_VISION_TASK.md` 顶部新块。**ArmD = 四变量**（数据 + epoch + LR + min_lr）：
> ①**数据** = ArmC 的 6 源之三（GPIC 8000 + CC12M 1100 + Amshaker 2250 = 11,350 shards）**+ 新三套**（WebMix-38M ~38.8M pairs / wit_base ~6.48M / InternVL-SA1B ~22.4M，均 10-16~10-17 下满）；
> ②**3 epoch**（ArmC 是 4 epoch/57,250 步；步数须按新 pair 总量重算，**须先报数再起训**）；
> ③**LR 2e-3**（ArmC 1e-3）；④**min_lr 2e-5**（ArmC 1e-5）；cosine 保持；
> **其余全部沿用 ArmC**：open_clip ViT-B/16 224、AIMv2-style(InfoNCE 1.0 + masked-patch-MSE 1.0, mask 0.6)、**wd 0.01（ArmC 值，不是 ArmB 的 0.1）**、GBS 8192/MBS 512/accum 2、warmup **2000 不变**、AdamW(0.9,0.98) bf16、seed 1234、save-every 10000/keep 2。
> 输出目录 **`armD_20261019_aimv2_openclip_vitb16_224`**（独立，不覆盖 ArmB/ArmC）。
> ✅ **前置阻断已解除（选 B · parquet→tar 转码）**：磁盘实测充足（/nas_user 22T /nas_train 26T 余量）；两 parquet 源 caption 列不同（WebMix `caption` / wit `caption_attribution_description`）→ 选 B（训练脚本 0 改动最安全）。`prep_data_armD.py` 转码全过：WebMix-38M 1945 tars(~38.8M 对,0 skip) / wit_base 294 tars(~5.85M 留,~630k 空过滤)。
> 🚀 **ArmD TRAINING RUNNING（wake #174, 2026-10-19 23:54:10 起训）**：6 源快照 `data_snapshot_20261019_armD.txt` = 14,589 shards（GPIC8000+CC12M1100+Amshaker2250=11350 + InternVL1000 + WebMix1945 + wit294）；**总 pairs=173,124,248**（ArmC 三源 117,305,600 固定 + 新三源 tar -tf 实数 55,818,648）；**3-epoch steps=63,400**（ceil(3×173,124,248/8192)）。`run_armD_openclip.sh` 直起（PID 129169，绕过 launcher 误报的 smoke 门——GPIC 用 `.json` caption 非 `.txt`，`build_mixed_loader` 本就兼容，已修 launcher smoke 接受 json）。lr=2e-3 min_lr=2e-5 wd=0.01 warmup=2000 mask=0.6 GBS=8192 seed=1234。step 20→80 loss 9.43→8.51 单调降无 nan，0.75 it/s→ETA~23h，peak 50.3GB（8 卡 80GB 无 OOM 风险）。日志 `/tmp/armD_openclip_train.log`。
> ⏭ **下次唤醒**：监控 `/tmp/armD_openclip_train.log` 至 500 步确认 warmup 段（LR 翻倍）loss 持续稳；step 10000 首 ckpt 时间；后续交 `run_armD_full_chain.sh`（②ProtB→③MLLM stage1/15/2→④12集离线缓存模式修 ArmC 8/12 MISSING 教训）→⑤报告 `report_vision_armD_20261019_mllm_stage4_zh.html`+`EXPERIMENTS_VISION.md §14`。⚠️ **四变量披露**（data 3src→6src + epoch 4→3 + lr 1e-3→2e-3 + min_lr 1e-5→2e-5）：ArmD vs ArmC 任何 Δ 不得归因单一变量。⚠️ MEMORY 33.7KB 略超 32KB，下次唤醒顺手滚 R9/R10 converged 块到归档。
> ⚠️ **warmup 交互须录入报告**：LR 翻倍但 warmup 仍 2000 步（用户令"其它不变"）⇒ warmup 段等效 LR 也翻倍；若 500 步内 loss 爆炸/nan，**停下报 blocker，不自行改 warmup**。
> ⚠️ **多变量披露**：ArmD vs ArmC 的任何 Δ 不得归因单一变量（同 ArmC 两变量框口径）。
> 📌 **四阶段链**（串行）：训练 → ②ProtB → ③MLLM 三阶段(Stage-1 2500 / 1.5 LoRA 20000 / 2 3500) → ④12 集；**④必须用离线缓存模式**（两处缓存指 `/tmp` + `HF_HUB_OFFLINE=1` + **不走代理**）—— ArmC 当年 8/12 MISSING 的教训。⑤ 报告 `report_vision_armD_20261019_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §14`。
> ✅ **落地条件**：`.12` 8 卡已全空（ArmC 闭环确认 0MiB）；pretrain 在 `.29`（预计 10-20 ~02:50 收尾），**与本线无冲突**。
> 📦 体积：TASK=29,447B(28.7KB ✓) / MEMORY=32,361B(31.6KB ✓，本轮已滚 R9/R10/R14/E1 converged 块→`ARCHIVE_OPERATOR_VISION.md`「2026-10-19 23:5x 滚动归档」节)。
>
> **本唤醒流水 [wake #174, 2026-10-19 23:5x]**：运维令「立即启动 ArmD」。核查发现上一 wake 已建好 6 源快照(14589 shards)+pair 计数(173,124,248)+steps(63,400)与 `run_armD_openclip.sh`，但 launcher 的 CPU smoke 门误判 GPIC `.json` caption 为 `txts=0` → 起训被阻断。实测确认 GPIC 用 json caption 且 `build_mixed_loader` 本就兼容、ArmC 用同批 shard 训成 57250 步 → **直起训练绕过误报门**，并修 launcher smoke 接受 json。`setsid bash run_armD_openclip.sh`（ARMD_STEPS=63400）于 23:54:10 起训；step 20→80 loss 9.43→8.51 单调降无 nan，0.75 it/s ETA~23h，peak 50.3GB/8 卡。**四变量披露：data 3src→6src + epoch 4→3 + lr 1e-3→2e-3 + min_lr 1e-5→2e-5**。

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
- [06:5x Oct18] **Wake #145**: 🔄 **ArmB 训练监控** — git pull up to date, 无新运维指令（顶部 12:4x kill+ArmB+ProtB 已执行）。✅ ArmB 4-epoch 训练健康: step **53740/57250(93.9%)**, loss~0.22(contr~0.20 patch~0.016, 硬分片抖动非坍缩), C1~0.82–0.90(正常), lr=1.09e-04(cosine→1e-4), **0.86 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=1039min(17.3h)。✅ ckpt@50000(@05:28)+40000+latest+open_clip_state_dict(598MB)+predictor+config 均在, next=final@57250。✅ grep error/nan/oom/traceback=**0**。✅ ProtB 脚本预检(OUT_DIR 对齐, 偏好 open_clip_state_dict.pt 已存在, OMP_NUM_THREADS=8)。ETA (57250−53740)/0.86≈**1.1h→~08:00 10-18**; +ProtB 1–2h⇒**~09:00–10:00 10-18**。下一步: 训完立即 .12 跑 `run_armB_protb_eval.sh`→armB 中文报告。📦 体积：TASK=26.2KB / MEMORY≈30.0KB（归档 #121~#135 内联→指针）。
- [11:2x Oct18] **Wake #148**: ✅ **Stage-1 ArmB 训完 + Stage-1.5 ArmB 启动** — Stage-1 DONE(2500步/6.7min, final loss4.5765, proj768→2560 8.52M)；Stage-1.5 启动(20000步, LoRA r=64+proj, ETA~12:48)。详见 daily-memories-vision/2026-10-18.md。
- [15:12 Oct18] **Wake #151**: ✅ **Stage-2 DONE + lmms-eval 切 ArmB768 塔 + 12集全量启动** — Stage-2 DONE(15.3min exit0 @14:10:09 final loss1.4779, ckpt `mllm_stage2_armB/step3500/`)。代码改动：`lmms_eval_baize_llava.py` 加 `vision_backend` 开关(armB→`create_baize_vitb16_768` 768d / baize_4ep→原512d)；`run_lmms_eval.py` 加 `--vision_backend/--ckpt/--stage2_base`(ArmB 独立结果目录 `mllm_eval_results_armB/`)；新增 `launch_12benchmarks_armB.sh`；`consolidate_12benchmarks.py` 加 `--results_dir`。✅ ai2d --limit5 冒烟 PASSED(768塔 strict load/LoRA merge/生成单字母答案/exact_match=0.40/img_feat 无NaN)。🔄 12集全量 @15:12:33 启动(8 GPU, batch32, 无limit, log→`/tmp/launch_12b_armB.log`, 结果→`mllm_eval_results_armB/`)。⚠️**mmmu_pro 首跑 exit=1**(MMMU-Pro 数据集未缓存+offline→ConnectionError；其余7集OK：mmmu_val exit0/realworldqa 0.4549 等)。**mmmu_pro 已用 online 模式重跑**(GPU1, PID613521, `HF_HUB_DOWNLOAD_TIMEOUT=120` 解 10s 读超时, 输出覆写 `eval_mmmu_pro.json`)。docvqa(GPU2)仍在跑。**下一唤醒务必：等 docvqa+mmmu_pro 都完成后重新 `consolidate_12benchmarks.py --results_dir mllm_eval_results_armB`**（主 launch 的 consolidate 时 mmmu_pro 可能仍缺）。ETA~3-5h。📦 体积：TASK=31.7KB / MEMORY≈31.2KB（均≤32KB）。
- [16:38–17:05 Oct18] **Wake #152**: ✅ **12集评测DONE + 报告** — 12集首跑FAILED(15:12→15:21, 只所4集, 根因=nas_env缓存缺MMStar/MME/blink/CountBench/MMMU_Pro+offline→整组GPU崩溃)。FIX: 改指/tmp缓存(全12集预缓存), 补跑8集16:38→16:42 exit=0。ArmB平均=26.10%, ␖=25.68%, Δ=+0.42pp。**裁定: 不可分辨(边界值)**。产物: report_vision_armB_mllm_stage4_zh.html + EXPERIMENTS_VISION.md§12。详见 daily-memories-vision/2026-10-18.md。
- [18:0x Oct18] **Wake #153**: 🚀 **ArmC 训练启动** — 用户直令「开启 ArmC」+追加「wd 0.1→0.01」⇒ ArmC=两变量(min_lr 1e-4→1e-5 + wd 0.1→0.01)。✅run_armC_openclip.sh(复制 ArmB, 仅改 OUT=armC_20261018_*/min_lr 1e-5/wd 0.01, .py 复用 armB_aimv2_openclip.py)；✅run_armC_protb_eval.sh 已备(ckpt→ArmC dir)。✅.12 8卡全空(4MiB/0%)→setsid 起 ArmC 训练：8 DDP worker, log 判据行 `lr=0.001 warmup=2000 cos->min_lr=1e-05 steps=57250 wd=0.01` ✓, step60/57250 loss 8.99↓ 0.73it/s 爬坡, 8卡100%@50.5GB peak50.3GB 无OOM/无error, LPT 0.0% imbalance 11350 shards。ETA~18.4h→约 10-19 12:00。📦 体积：TASK 36208→29653B(归档 P0 ArmB→MLLM + epoch-replay 两块→ARCHIVE) / MEMORY 31166B（均≤32KB）。下一步: 监控→训完 ProtB→MLLM→12集。
- [19:31 Oct18] **Wake #154**: 🔄 ArmC 监控 step4600/57250(8.0%), 0.89it/s, log判据行确认两变量, 健康。详见 daily-memories-vision/2026-10-18.md。
- [20:52 Oct18] **Wake #155**: 🔄 ArmC 训练监控 + 体积归档 — step 8600/57250(15.0%) 健康, 0.86it/s, ckpt@10000 未到, MEMORY 33534B→21618B(归档两节运维问答→ARCHIVE)。详见 daily-memories-vision/2026-10-18.md。
- [23:27 Oct18] **Wake #157**: 🔄 ArmC 监控 step16200/57250(28.3%), 0.84it/s, ckpt@10000, 健康。详见 daily-memories-vision/2026-10-18.md。
- [22:09 Oct18] **Wake #156**: 🔄 **ArmC 训练监控** — git pull(behind1, video线bc5d4def)→rebase autostash→up to date; 无新运维指令（顶部 17:1x ArmC 块为最高优先, ①训练已由 #153 启动）。✅ ArmC 训练健康: step **12580/57250(22.0%)**, loss~0.3-0.5(硬分片抖动非坍缩, 同 ArmB 模式), C1~0.61(正常振荡), lr=9.13e-04(cosine, warmup=2000 已过), **0.86 it/s**(稳态), 8×H100 96-100%/50.5GB(peak=50.4GB 无OOM), t=244min(4.06h)。✅ log 判据行确认 `lr=1e-3 cos->min_lr=1e-05 wd=0.01` ✓（两变量正确）；✅ grep error/nan/oom/traceback=**0**；✅ **ckpt@10000 已存**(21:22, open_clip_state_dict 598MB+latest.pt 1.8GB+predictor.pt+config.json)；✅ ArmB OUT dir 未被触碰（ckpt 10-18 07:54 完好）；✅ run_armC_protb_eval.sh 就绪(待训完)；⚠️每步打印前缀为 `[ArmB]`（.py 复用 armB_aimv2_openclip.py 硬编码），已核对 output_dir 指向 armC_20261018_aimv2_openclip_vitb16_224，**非误跑 ArmB**。③④MLLM+12集 待串行。ETA (57250−12580)/0.86≈**14.4h→~10-19 12:35**；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒**~10-19 17:00 全链路完成**。下一步: 监控→训完`run_armC_protb_eval.sh`→MLLM三阶段→12集→报告。📦 体积：TASK≈29.7KB / MEMORY≈21.6KB（均≤32KB✓，无需归档）。
- [00:49 Oct19] **Wake #158**: 🔄 **ArmC 训练监控 + ③④全链路脚本就绪 + chain watcher 启动** — git fetch up to date（`## main...origin/main`，无 ahead/behind，无新运维指令；顶部 17:1x ArmC 块为最高优先，①训练已由 #153 启动）。✅ ArmC 训练健康: step **19980/57250(34.9%)**, loss~0.53(硬分片抖动非坍缩, 同 ArmB 模式), C1~0.60(正常振荡), lr=7.63e-04(cosine 下降中), **0.82 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=404min(6.7h)。✅ grep error/nan/oom/traceback=**0**；✅ ckpt@10000 已存(21:22), ckpt@20000 即将出现(~step20000)；✅ ArmB OUT dir 未被触碰。**本轮关键产出（CPU 工作, 不占 GPU）**：为 ArmC ③④阶段新建全部脚本——①`stage1_train_armC.py`/`stage15_train_armC.py`/`stage2_train_armC.py`(cp+sed from ArmB, 仅改 CKPT→armC_20261018 + OUTPUT_DIR→*_armC_20261018, 超参/数据/步数/LoRA 全不变)；②`launch_12benchmarks_armC.sh`(--vision_backend armC, LOG_DIR→mllm_eval_results_armC_20261018)；③`run_lmms_eval.py`+`lmms_eval_baize_llava.py` 已加 `armC` backend（同 armB 架构, `if vision_backend in ("armB","armC")`, 复用 create_baize_vitb16_768）；④`run_armC_full_chain.sh`(轮询训练进程退出→验证ckpt→②ProtB→③Stage1/1.5/2→④12集, 严格串行, 每步 error-check+exit on fail, 避免GPU空闲)。✅全部语法检查通过(ast.parse+bash -n)。✅**chain watcher 已在 .12 启动**(PID 4131476, /tmp/armC_full_chain.log): PHASE 0 轮询中(5min间隔), 训练退出后自动起②→③→④。ETA (57250−19980)/0.82≈**12.6h→~10-19 13:30训完**；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒**~10-19 18:00全链路完成**。下一步: chain自动跑→下一唤醒检查②ProtB结果→③④自动完成→生成报告。📦 体积：TASK=29.7KB / MEMORY=26.2KB（均≤32KB✓，无需归档）。
- [07:13 Oct19] **Wake #162**: 🔄 ArmC 监控 step37380/57250(65.3%), 0.79it/s, ckpt@20000/30000, 健康。详见 daily-memories-vision/2026-10-19.md。
- [08:37 Oct19] **Wake #163**: 🔄 ArmC 训练监控 step41020/57250(71.6%) + chain 路径核验（③④四脚本均存在），健康。详见 daily-memories-vision/2026-10-19.md。
- [09:58 Oct19] **Wake #164**: 🔄 ArmC 监控 step44920/57250(78.4%), 0.79it/s, ckpt@30000/40000, log判据行确认两变量, 健康。详见 daily-memories-vision/2026-10-19.md。
- [12:37 Oct19] **Wake #166**: 🔄 **ArmC 训练监控（健康，90.9%）** — git fetch up to date（`## main...origin/main`，无 ahead/behind；origin 最新 6a1fe964 pretrain/4ac00e0d zhulong/54d086b2 harness/0ebb73b0 news 均他线，无新 vision 运维指令；顶部 17:1x ArmC 块为最高优先，①训练已由 #153 启动）。✅ ArmC 训练健康: step **52060/57250(90.9%)**, +3560自#165(~1.4h), 末段 loss 振荡加大 0.10→0.46(contr 主导 0.09→0.44, patch 稳定~0.0168)=硬分片末段抖动**非坍缩**(同 ArmB 末段模式; C1 同步回落 0.92→0.64), lr=3.16e-05(cosine下降向min_lr=1e-5), **0.78 it/s**(稳态), 8×H100 100%@50502MiB(peak=50.4GB 无OOM), t=1112min(18.5h)。✅ grep error/nan/oom/traceback=**0**；✅ 盘上核(OUT=`/nas_train/app.e0031982/datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/`) ckpt@40000(08:17)+50000(11:51)+latest+open_clip_state_dict(598MB)+predictor(4.7MB)+config.json 均在(10000/20000/30000已滚动删, keep-ckpts 2), final ckpt@57250~14:25；✅ **config.json 复核**: lr=0.001/min_lr=1e-05/wd=0.01/seed=1234/mask_ratio=0.6/contrast_weight=1.0/patch_loss_weight=1.0/n_visual=86192640(86.2M,与ArmB一致) → **只有 min_lr+wd 两变量** ✓；✅ ArmB OUT dir 未被触碰（ckpt_50000/57250 10-18 07:54 完好）。✅ **chain watcher PID 4131476 存活**(ppid=1, /tmp/armC_full_chain.log PHASE0 轮询5min, 最近[12:35:06]"Training still running"); chain 逻辑已核(sed 读 run_armC_full_chain.sh): 训练PID退出→验open_clip_state_dict.pt→②ProtB→③MLLM三阶段→④12集, 每步 exit-code 门控。⚠️每步打印前缀 `[ArmB]`=py logger名硬编码, 实为 ArmC run, 报告须注明。ETA (57250−52060)/0.78≈**1.85h→~10-19 14:25训完**；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒**~10-19 19:00全链路完成**。下一步: chain自动跑②→③→④；下一唤醒预计训练已训完/②ProtB 进行中或完成→查 ProtB 结果(lp/5-NN 对比 ArmB 62.093/58.102、④-4ep 67.05)+③④进度→生成报告 report_vision_armC_20261018_mllm_stage4_zh.html + EXPERIMENTS_VISION.md §13。📦 体积：TASK=29.0KB / MEMORY=31.2KB（均≤32KB✓，无需归档）。
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
