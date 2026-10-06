# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | 🚀 **R12b 全量数据 AIMv2 训练中**（fresh run, 272k 步≈2 epoch, 7527 shards, 12:54 起, step~46750/272000 ~17%, loss~2.4, C4=OK, ~5300 img/s 稳态/NFS 波动降至 ~3000, 4 ckpts 已存, ETA~21:00–23:00）. ✅ 论文 §6 改写完成. ✅ 前置 AIMv2 提速归因实测完成. ✅ 两份 HTML 报告+方向建议已交 |
| WAITING | 1（**R12b 训练中** step~46750/272000 ~17%, loss~2.4, C4=OK, 4 ckpts(step10k/20k/30k/40k 510MB each). 训练完自动跑 IN-1k eval → scaling 曲线. ETA~21:00–23:00. 所有交付物已完成, 仅待训练结束+eval）|
| ERROR_COUNT | 3（① R9 w512 首跑 crash：损坏 jpg → data.py 修复 ② 续跑首试 crash：r9_train.py `log()` → 改 `print()` 修复 ③ 8-GPU 并行 eval NFS 争用卡死 → 改 4-GPU r12_single_eval.sh） |
| BUDGET_USED | R2–R12 累计 ≈215 GPU·h + 归因实测 ~0.5 GPU·h + **R12b 训练中**（~7.7h×8卡≈61.6 GPU·h 预计） |
| 更新 | **2026-10-06 14:52（R12b 心跳巡检#2: step~46750/272000 ~17%, loss~2.4(contrast~2.2/patch_mse~0.23), C4=OK, 4 ckpts(step10k/20k/30k/40k 510MB each), 7/8 GPU util 100%(GPU0 transient 0%), mem 16.5GB each, NFS 波动 img/s 5600→3000. ETA~21:00–23:00(NFS 波动大). 所有交付物已完成. 📦 TASK=24KB/MEMORY=10KB）· *[更早见 daily-memories-vision/2026-10-06.md]* |
| WINNER | OpenVision2（R8 六架构四指标第一；R9/R10 证「塔越小越高」，w512=126.8M 是既有对比基线，不改架构排名） |

## R9 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND9.md）

- 阶段一：w512/w768/w1024 lp = 6.10/3.63/1.03% → 选 **w512（126.8M）**。阶段二：w512×108k=55.3M，lp 峰值 7.70%@51.2M。
- **scaling 拟合**（11 点 R²≈0.94）：幂律 `acc=0.251−0.864·N^−0.090`（渐近 **25.1%**）；外推 20% 需 41 万亿样本 → **本地 ≈118M 上限够不到**。
- **结论**：瓶颈在数据量与目标函数（AIMv2 ≈120 亿对 vs 我们 649× 少），非架构。

## R10 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND10.md）

- 2D 拟合（19 点 R²=0.980）：M 边际效应**全区间为负** ≈ −2.2 lp pp/参数翻倍 → 数据受限区间**加宽塔是负收益**。
- **w384@15.36M=7.99% 为全部宽度最高**；最优 M 仍在观测下界（71.5M）之下 → 无饱和点、更小塔持续更优。

## R14 官方仓库调研（✅ 全部完成，2026-10-03）

- CPU-only 源码普查，与 R10-③ denseM 训练并行。产物：`VISION_OFFICIAL_REPOS_SURVEY.md`（①目标②数据③config④结构差异⑤可复用资产⑥LICENSE⑦三清单）。
- ✅ 两个 ⭐⭐⭐ 仓库源码普查完成（上一 cycle）：**OpenVision**（JAX/TPU，官方 ViT-L/16 = w1024/d24/h16；文本 = BERT-128 + LLaMA3 dense caption + caption decoder + keep_ratio=0.35）；**ml-aim/AIMv2**（仅模型接口，无训练/损失/数据；LICENSE = Apple Sample Code，🔴 不可 COPY）。
- ✅ 第二阶段（本轮）全部核毕：
  - **OpenVision2 权重 = ✅ 已放出且真带 caption decoder**：HF `UCSC-VLAA/openvision2-vit-{so400m,large,huge,giant}-patch14-{224,336,384,448}-vision-only`；含 `caption_decoder.safetensors` + `text_decoder_config.json`（concat/prefix-LM，非 CoCa cross-attn）。🔑 官方 = **patch14/d24**，我们 = **patch16/d30**（models.py:170）→ R13 需另建官方结构塔才能 load。
  - **FastVLM** = ✅ `apple/ml-fastvlm`（FastViTHD 1024² conv-hybrid RepMixer）；LICENSE = Apple Sample Code（research-only，不可抄）。
  - **MambaEye** = ✅ `usingcolor/MambaEye`（MIT）：纯 Mamba2、**小模型监督分类**（非对比）；**MoE-ViE** = ✅ `facebookresearch/moe_vie`（CC BY-NC 4.0）：CLIP 风格 MoE-ViT，官方权重 HF；**iGVLM(AdaLN)/TuringViT** = 🚫 **未找到官方实现**（iGVLM 同名 IG-VLM 是视频QA；TuringViT 仅项目主页）。
- 关键产出（对 R13/R12）：官方 MoE-ViE/FastVLM/MambaEye/AIMv2 权重均可作「官方 vs 自研」对照标尺；OpenVision2 官方是 patch14/d24，需建官方结构塔。

## E1 GPIC 规模实测（✅ 完成，2026-10-03）

- 抽 **8 个 tar 均匀抽样**（index 0..1212）实测：**12,537 图文对/tar**（稳定 ±2%）→ **GPIC 全量 ≈ 100.3M**（证官方 100M 卡；旧「5 tar=86M」少计 png 作废）；**已下 1213/8000 tar ≈ 15.2M**。
- `caption_type` mix：short **45.0%** / medium 45.1% / long 9.0% / tag 1.0% → **可训练 short 子类：全量 ≈45M / 已下 ≈6.8M**。
- 🔑 **C1 口径定案**：R9 用过 18.5M / 盘上现有 ≈32M / 本地全量 ≈118M（动态、仍在下载）——与 `r9_scaling.py --local-cap-m default=118.0` 一致；R11-E「同 N」可比区间被压到 ≈6.8M（short 已下 < 18.5M），须如实说明。已回填 `VISION_ARCH_FRONTIER_2026.md §5`。

## R11-L / R11-L2 / caption-weight / R11-F / R11-G / R11-H / R12 / 3-epoch 全部完成

> 📦 以上全部已闭合实验（R11-L 四臂→R11-L2→caption-weight→R11-F→R11-G→R11-H→R12→3-epoch 续跑）的详细流水已滚动归档 → `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（**原文未改**）。**结论以 `EXPERIMENTS_VISION_ROUND11.md` + `EXPERIMENTS_VISION_ROUND12.md` 为权威。**

**一句话结论**：R11-L 四臂（SigLIP/LocalLoss/CoCa/基线）**无一翻盘**；R11-L2 文本塔解冻（LoRA）**未翻盘**（−0.80 pp）；caption-weight 三点消融 → **caption 监督与 IN-1k 正交**；R11-F 数据源横比 → GPIC short/medium/short+medium **无显著差异**；⭐ **R11-G AIMv2 长跑翻盘**（lp@55.3M=19.76% vs 基线 7.40%，R²=0.91，渐近 >>25.1%）；R11-H 纯 AR **无翻盘**（翻盘依赖对比项）；R12 全量 58.8M 1.05 epoch lp@61.4M=17.57%（< R11-G 同 N）；3-epoch 续跑 344k/176M lp=20.27%，35 点 scaling R²=0.94，非单调 7/34，a 撞上界不可定。

## AIMv2 提速归因实测（✅ 完成，2026-10-06 12:33–12:44）

> 运维指令「运维前置 · AIMv2 提速」（已归档 → `ARCHIVE_OPERATOR_VISION.md`）。目的：bs 64/128/256 归因 + num_workers 扫描 → 判断瓶颈是数据/IO 还是算力。详见 `EXPERIMENTS_VISION_ROUND12.md §1`。

### batch size 扫描（nw=6 固定）

| BS | Global | steady img/s | ms/iter | Mem(GB) | GPU util |
|---:|---:|---:|---:|---:|:---|
| 64 | 512 | **4993** | ~102 | 16.5 | 62–83% (~70%) |
| 128 | 1024 | **6293** | ~134 | 26.8 | 49–95% |
| 256 | 2048 | **8314** | ~250 | 47.6 | 48–100% |

### num_workers 扫描（bs=64 固定）

| NW | steady img/s | Notes |
|---:|---:|:---|
| 6 | **4993** | baseline |
| 12 | **4262** | 更差（NFS 争用） |
| 16 | **5311** | 略好（噪声范围） |

### 诊断：**bs=64 下数据/IO 受限（非算力受限）**

1. GPU util ~70%（未饱和）→ 符合「util≲70% = 数据/IO 受限」判据
2. image/s 随 MBS 上升（4993→8314, +66%）= 每步开销摊销，**非**算力受限标志
3. ms/iter 亚线性增长（64→256 = 4×, ms/iter 2.45×）→ 混合瓶颈，以数据/IO 为主
4. 显存远未满（16.5/81.6 GB = 20%）；num_workers 无显著效果（NFS 带宽是瓶颈）
5. 无本地 NVMe；1.7 TiB RAM 但数据 ~742 GB（预热增益有限，NFS 波动仍存）

### 处方：保持 bs=64 / global 512 / nw=6

- ❌ 加 MBS → 改 recipe → 不并入 scaling 曲线
- ❌ 加 num_workers → NFS 争用（nw=12 实测更差）
- ❌ 无本地 NVMe 可用
- **当前 ~5000 img/s 是 NFS 架构下可达到吞吐率**

### 全量训练时长估算（实测 img/s）

- 总 unique pairs ≈ 58.8M；1 epoch ≈ 114,844 步
- 实测 ~5000 img/s → **1 epoch ≈ 3.3h**；保守 ~4500 img/s → **1 epoch ≈ 3.7h**
- R12 3-epoch 实测平均 4470 img/s → 1 epoch ≈ 3.7h（吻合）
- **>1 epoch？是。** 2 epoch ≈ 7.2h, 3 epoch ≈ 10.8h
- 从零 1 epoch ≈ 29.6 GPU·h；从零 3 epoch ≈ 88.8 GPU·h

### 脚本路径

- `vision/r12_throughput_bench.sh`（bs 扫描）+ `r12_throughput_bench_128_256.sh` + `r12_throughput_bench_nw.sh`
- 日志：`/tmp/bench_bs{64,128,256}.log` + `/tmp/bench_nw{12,16}.log`
## 本唤醒流水

- [12:33–12:44] **AIMv2 提速归因实测**：bs 64/128/256 各 250 步 + nw 6/12/16 各 250 步 → bs=64 steady 4993 img/s (GPU util~70%), bs=128 6293, bs=256 8314; nw 6=4993, nw=12=4262(更差), nw=16=5311 → **诊断数据/IO 受限**, 1 epoch≈3.3–3.7h. 详见 `EXPERIMENTS_VISION_ROUND12.md §1`.
- [12:45] 归档 R11-L→3-epoch 完成段到 `daily-memories-vision/2026-10-06.md`（MEMORY 31KB→9KB 腾位）；写 `EXPERIMENTS_VISION_ROUND12.md`.
- [12:50] commit 923bf898 pushed（归因实测 + 归档）. 被 ops 的 d78f01ca 误回滚 → ops 50621368 修复.
- [12:54] **R12b 全量数据 AIMv2 fresh run 起跑**：272k 步≈2 epoch, 7527 shards (GPIC=4176+CC12M=1100+Amshaker=2250), bs=64×8=512, nw=6, seed=1234, loss=aimv2. step 300: loss=4.21, ~5100 img/s, GPU util~70%. ETA ~20:30. 日志 `/tmp/r12b_fulldata_aimv2.log`.
- [13:37] **论文 §6 改写**（运维指令 2026-10-05 晚 ②, R12b 稳态后授权）：`6_vision_encoder.tex` 2 处改动 — ① line 96 追加 3-epoch 延伸句（176M/20.27%/R²=0.94/非单调/a→1.0）② Boundary 段全替换（stale "currently underway" → completed 35-point scaling, 176M 无饱和, full-data mix matched-N 更低效, 交互效应确认）. diff 摘要 → `EXPERIMENTS_VISION_ROUND11.md §20`. R12b step~21900 C4=OK.
- [14:18] **R12b 心跳巡检#1**：step 36300/272000 ~13%, loss~2.6 (contrast~2.4, patch_mse~0.21), C4=OK. 3 ckpts 已落盘（step10k/20k/30k, 487MB each）. 8 GPU util 67-88%, mem 16.5GB each. NFS 波动 img/s 5300→2400（正常波动, GPU 未崩）. ETA~20:30–21:10. 所有交付物（HTML 报告×2 + 论文 §6 + 方向建议 + 归因实测）均已完成并提交.
- [14:52] **R12b 心跳巡检#2**：step~46750/272000 ~17%, loss~2.4 (contrast~2.2, patch_mse~0.23), C4=OK. 4 ckpts 已落盘（step10k/20k/30k/40k, 510MB each）. 7/8 GPU util 100%（GPU0 transient 0% — 数据加载瞬时）, mem 16.5GB each. NFS 波动 img/s 5600→3000（正常波动）. 平均 ~396 steps/min, 剩余 225k 步, ETA~21:00–23:00（NFS 波动大, 不确定）. 训练健康, 无需干预. 📦 体积：TASK=24KB / MEMORY=10KB（无归档）.

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
