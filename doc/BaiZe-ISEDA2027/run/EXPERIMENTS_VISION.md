# EXPERIMENTS_VISION.md — BaiZe Stage(iii) 视觉编码器预训练对比

> 四架构（500–600M）从零预训练公平对比。统一 open_clip(3.2.0) + SigLIP + 固定 text tower + 统一子集。

## ⭐ 最终胜出结论（R4–R8 修复 recipe，2026-10-02，**权威**）

> ⚠️ 本节为**最终结论**，覆盖下方「S0–S9 / converged」各节的 R1/R2 旧读数——那些旧读数**已因表征坍缩与 lr=1e-3 cosine 伪影作废**（详见 `EXPERIMENTS_VISION_ROUND2~ROUND8.md`）。数据与 recipe 的演进：R4 修 recipe（冻结 CLIP-768 文本塔 + InfoNCE）→ R5 架构/分辨率 → R6 77 裁定 → R7 数据裁定（GPIC short）→ R8 扩 6 架构 + IN-1k。

**胜出架构：OpenVision2（纯 Attention ViT，505.2M）—— R8 六架构重比，四指标全第一**

| 架构 | loss@3k | C1（同塔off-diag） | IN-1k zs top-1 | IN-1k lp top-1 | 训练 img/s | 判定 |
|:--|--:|--:|--:|--:|--:|:--|
| **OpenVision2** | **4.8646** | **0.2875** | **0.95%** | **1.14%** | 3051.8 | ✅ 胜出 |
| MoE-ViE（moevie） | 5.5580 | 0.4109 | 0.35% | 0.28% | 1225.7 | ✅ 健康（激活 222M） |
| AIMv2（等参改编） | 5.6370 | 0.3931 | 0.38% | 0.25% | **3392.5** | ✅ 健康（吞吐最快） |
| FastViTHD（等参改编） | 5.6683 | 0.4494 | 0.39% | 0.27% | 2097.4 | ✅ 健康（conv-hybrid 无优势） |
| MambaEye（纯 SSM） | 6.2507* | 1.0000 | 0.10% | 0.10% | 949.5 | ❌ @300 坍缩 |
| DeepEncoderV2（Attn+SSM） | 6.2513* | 1.0000 | 0.10% | 0.10% | 1864.5 | ❌ @300 坍缩 |

- **三条最终结论**：① 修复 recipe 下**架构有真实差异**（loss 4.8646~5.6683、IN-1k 0.95%~0.39% 可分），OpenVision2 全指标第一 → 作废旧「loss 与架构无关」；② 坍缩是 **SSM 特异**（含 SSM 子结构即 @300 坍缩，纯 Attention 系 4 架构全健康）；③ **IN-1k（frozen trunk zs/lp）成功替换退化的 R@1**（旧 R@1=1/5000 chance 零区分度）。
- ⚠️ **C2 限定（2026-10-03）**：上表 6 架构**全是自研 from-scratch 等参改编（非官方模型）**（`run/vision/models.py` 头行自证）。故「SSM 坍缩」只能表述为**「我们 recipe（冻结语义文本塔 + InfoNCE）下、我们自研改编版的坍缩」**，🚫 **不得**推广成「官方 MambaEye/DeepEncoderV2 会坍缩」。
- **最终 recipe**：Stanford **GPIC `short`**（20 tok / 0% 截断）+ InfoNCE + 冻结 `clip-vit-large-patch14-336` 768 维文本塔（context 77）+ lr 3e-3 / warmup 20 / seed 1234 / bf16 / bs64 × 8 卡 = 512 负样本。
- 详见 `EXPERIMENTS_VISION_ROUND8.md`（§4 六表 + §8 排名 + §9 回填建议）。

**完整可复现训练命令（R8 胜出架构）**：

```bash
conda activate py310
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

# 单架构（胜出 OpenVision2）完整训练：3000 步 @224/16 bs64，GPIC short，冻结 CLIP-768 文本塔
python -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
     --master_addr=127.0.0.1 --master_port=$((29400 + RANDOM % 1000)) \
     r7_train.py --tower openvision2 --steps 3000 --resolution 224 --patch 16 \
     --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
     --data '/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar' \
     --data-source gpic --output-dir /nas_train/app.e0031982/datasets/baize-vision/out/R8_openvision2 \
     --log-every 50 --probe-every 300 --probe-n 128 --num-workers 2 \
     --eval-data '/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'

# 六架构串行 + 末了 IN-1k zero-shot / linear-probe 评测
bash r8_run.sh 3000
```

---

## ⭐ R9 追加结论：scaling law（数据扩容 + 长训练，2026-10-03）

> R9 用「缩塔先导 + 长训练」把数据从 ~2.77M 对扩到 ~18.5M 对、把步数拉到 108k，画出 IN-1k 随样本的 scaling 曲线并外推。**不改 R8 的架构排名**（OpenVision2 仍胜出）；详见 `EXPERIMENTS_VISION_ROUND9.md` §4–§5。

- **缩塔先导（阶段一，3 臂 × 30k）**：OpenVision2 × width{512,768,1024}，IN-1k lp = **6.10% / 3.63% / 1.03%** → **塔越小、每样本效率越高**（505M 在 ~15.4M 样本下严重欠拟合，loss 反高 4.92）→ 选 **w512（126.8M）**。
- **长训练（阶段二，w512 × 108k 步 = 55.3M 样本）**：无坍缩（C1≈0.36 / C2_gap≈+0.10 / loss_ema 5.99→**3.71**，steady 2904 img/s）；IN-1k lp 峰值 **7.70%**@51.2M（末点 7.40%）、zs top-1 3.59%、top-5 11.47%。
- **scaling 拟合（11 点，R²≈0.94）**：幂律 `acc=0.251−0.864·N^−0.090`（渐近 **a=25.1%**）；对数线性 `acc=−0.229+0.0398·log10(N)`。
- 🔴 **外推结论（核心决策依据）**：目标 20% 需 **对数线性 619 亿样本（本地 ≈118M 上限的 ~525×）/ 幂律 41 万亿样本**；40%/60% 在幂律下**不可达**（渐近 25.1%），对数线性下需 6.6×10^15 / 7.1×10^20 样本。→ **此从零对比学习路线在本地数据规模下够不到 20%+**。
- **量级对照**：AIMv2 ≈120 亿对 → 88.7%；我们 55.3M → 7.7%（**649× 数据缺口**，严禁并列）。瓶颈在**数据量与目标函数，非架构**。
- 📌 **建议路线**：要抬高 IN-1k 只能 ① 加载大规模预训练权重（等价 120 亿对）② 换重构型目标（MAE/MIM，无 text 塔无坍缩）③ 用现成编码器做 Stage(iii) 选型。

### 🔧 C1 数据量口径修正（2026-10-03 · E1 实测 · 必做修正）

> 原「本地 53M 唯一对上限」是 `r9_scaling.py` `--local-cap-m default=53` 的**假设**、非实测。E1 抽 8 个 GPIC tar 实测 → 每 tar ≈12,495 唯一图文对（json=图 1:1，jpg≈11k + png≈1.5k）。三类分母统一如下（**数据仍在下载，动态值**）：

| 分母 | 值 | 组成 |
|:--|--:|:--|
| **R9 用过** | ≈18.5M | CC12M ~11M + Amshaker ~6M + LLaVA/CC3M ~1.15M + coco/vg ~0.3M（不含 GPIC train） |
| **盘上现有** | ≈33M | 18.5M + GPIC train 已下 1195 tar × 12.5k ≈ 14.9M |
| **本地全量** | ≈118M | GPIC 全量 8000 tar × 12.5k ≈ 100M + CC12M ~11M + Amshaker ~6M（+LLaVA/CC3M ~1.15M） |

- **重算关键缺口**（AIMv2 ≈120 亿对）：649×（对 18.5M）→ **359×（对 33M）→ 102×（对 118M）**；「20% 需 619 亿样本」= **~525× 本地 118M 上限**（原「1168× the 53M」是低估了 cap）。
- ⚠️ **结论不变**：即便用真实 cap ≈118M，此从零对比路线**仍够不到 20%+**（619 亿 vs 118M = ~525×）。瓶颈在数据量与目标函数，非架构。
- 证据：GPIC 实测命令 `tar -tf gpic_train_NNNNN.tar | grep -c '\.json$'`（8 tar 采样，见 `EXPERIMENTS_VISION_ROUND10.md` / 当日日志）。

## ⭐ R10 完成：M 轴 scaling law（模型规模轴，2026-10-03）

> 补全 R9「只扫了数据侧 N」的缺口，复用阶段一三档塔宽 ckpt 补 M 轴，拟合 (N,M) 二维 scaling。详见 `EXPERIMENTS_VISION_ROUND10.md`。

- **R10-①（✅）回收阶段一 12 点 IN-1k**：w512/w768/w1024 × step{10k,20k,30k}，lp 终点（@15.36M）= **6.08% / 3.63% / 0.93%** ——单调下降，印证「塔越小每样本效率越高」。
- **R10-②（✅）2D 拟合（3 点 M 轴，R²=0.980）**：`acc=-1.737+0.333·log10(N)+0.185·log10(M)-0.036·log10(N)·log10(M)`；**M 边际效应全区间为负 ≈ −2.2 lp pp / 参数翻倍**。
- **R10-③（✅）补密 M 轴 → 5 点重拟合（R²=0.960）**：w384(71.49M)+w640(197.80M) 各 30k 步（同数据/recipe）；**w384 @15.36M lp=7.99% 为全部宽度最高**（w512 5.44~6.08 / w640 3.62 / w768 3.63 / w1024 0.93）→ 更小塔持续更优、**无饱和点**；小塔吞吐更高（w384 6583 vs w640 2418 img/s）。最终：`acc=-1.452+0.298·log10(N)+0.150·log10(M)-0.0318·log10(N)·log10(M)`，M 边际 ≈ **−2.2~−2.4 pp/参数翻倍**。
- **核心结论（已定）**：数据受限区间（N≤55.3M）**加宽塔是负收益、应继续向下探塔**；与 R9 N 轴结论合一 → 从零对比学习在本地 ≈118M 上限下，无论调 N 还是 M 都够不到 20%+，瓶颈在数据量与目标函数。
---

## 胜出结论（S0+S1+S2+S3 汇总 · ⚠️ R1/R2 旧读数，已因坍缩/lr 伪影作废，仅作历史）

**胜出架构：OpenVision2（纯 Attention ViT，w1024·d30·h16·mlp4096，505.0M）**

- P0 三硬指标：训练吞吐 **2139 img/s（最优，S3 干净实测）**、推理 **153.7 img/s / 6.51ms（最优）**、最终 loss 4.4540（四架构并列 ~4.45–4.47）。
- 关键量化洞见（S3 长地平线修正）：把训练延长到 5k–10k 步后，四架构 loss 全部从 S1 的 6.7342 平台继续跌破至 **~4.45–4.47**，且架构间 loss 差 <0.02（噪声级）→ **架构在 loss 上不可区分**，选择完全由吞吐/延迟决定。
- 🔑 S1「四架构 loss 全 6.7342 平台」是 **cosine LR 坍缩伪影**（`--steps 1000` 令 cosine 在 ~700 步就把 LR 从 1e-3 衰减到 ~2.6e-4→1e-5@1000，loss 卡死），**非架构等价**。S3 用 `--steps 10000`（cosine 跨 10000 步），step700 LR 仍 ~9.9e-4，loss 继续降：6.85@500→5.92@1000→4.45@5k–10k。
- 吞吐/延迟差异由结构决定（224/16 · 196 token 小序列）：纯 Attention 最优（2139 img/s / 6.5ms）；SSM 与 MoE 在 196 token 下**开销主导、吃不到长序列红利**（DeepEncoderV2 1459 img/s / 17.8ms，MambaEye 790 img/s / batch1 卡死，MoE-ViE 852 img/s / 141ms）。

> ⚠️ 吞吐测量带病（共享集群）：S1/S2 与另一项目 `nemo_experiments` 的 s1_01/s2_01（arch=mamba2，8×H100）并发，存在争用。DeepEncoderV2 训练稳态 578 img/s 系「误触发 openvision2 进程争用」污染，其干净稳态 ≈1430–1450 img/s（step300–725）。相对排序不受影响。

## 环境与配置

- BASE_DIR：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027`；实际代码在 `run/vision/`（models.py / data.py / train.py / prep_data.py / run_train.sh / run_s1.sh）
- 环境：conda `py310`（CUDA 12.8 / PyTorch 2.8.0 / open_clip 3.2.0 / torchvision 0.23 / mamba_ssm / webdataset 1.0.2 / flash_attn）
- GPU：6×H100 80GB（DP6，TORCH_NCCL）。四架构同卡数、同 batch、同 seed。
- 数据：LLaVA-OneVision-1.5 Mid-Training（parquet）切成统一子集 `imagenet/EN` 500K 对 →
  webdataset tar（`/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar`，25 shard × 20K）
- 默认配置（S1 锚点）：cls=224 / patch=16 / SigLIP / lr=1e-3 AdamW(0.9,0.95) / warmup 100 + cosine /
  seed=1234 / bf16 / batch=32×6=192 / text tower = 12L·512w·8h（四架构共用随机 init）

## 四架构实测参数量（numel，target 500–600M）

| 架构 | 类型 | 参数量 | 激活参数 | 备注 |
|:---|:---|:---|:---|:---|
| OpenVision2 | 纯 Attention ViT | 505.0M | 505.0M | w=1024 d=30 h=16 mlp=4096 |
| MambaEye | 纯视觉 SSM（Vim 双向） | 534.9M | 534.9M | w=1024 d=40 d_state=16 expand=2 |
| MoE-ViE | 稀疏 MoE | 505.2M | 222.0M | w=1024 d=30，8 expert×ff512，top-2 |
| DeepEncoderV2 | Attn+SSM 混合（AAMM） | 516.9M | 516.9M | w=1024 d=34 混合 |

## S0 冒烟（15 步，6 卡 batch32）

| ID | 架构 | 参数量 | loss@15 | ms/iter | image/s | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| S0-A | OpenVision2 | 505.0M | 7.797 | 127.5 | 1505 | ✅ RUNNABLE |
| S0-B | MambaEye | 534.9M | 7.827 | 510.1 | 376 | ✅ RUNNABLE |
| S0-C | MoE-ViE | 505.2M(222M) | 9.254 | 1371.6 | 140 | ✅ RUNNABLE(未达稳态) |
| S0-D | DeepEncoderV2 | 516.9M | 7.794 | 247.0 | 777 | ✅ RUNNABLE |

> 注：15 步含 cudnn autotune/首步惰性初始化，MoE 的 ms/iter 尚在下降未达稳态，S1(1000步) 会重测 steady-state。

## S1 主训练（1000 步 × 4 架构，默认配置）

| ID | 架构 | 参数量 | 状态 | 最终loss | 训练image/s | 耗时 | GPU·h |
|:---|:---|:---|:---|:---|:---|:---|:---|
| S1-A | OpenVision2 | 505.0M | ✅ 完成 | 6.7342 | 1491 | 235s | 0.39 |
| S1-B | MambaEye | 534.9M | ✅ 完成 | 6.7342 | 398 | 642s | 1.07 |
| S1-C | MoE-ViE | 505.2M(222M) | ✅ 完成 | 6.7342 | 443 | 531s | 0.88 |
| S1-D | DeepEncoderV2 | 516.9M | ✅ 完成 | 6.7342 | 578* | 303s | 0.51 |

> *DeepEncoderV2 训练吞吐被「误触发的 openvision2 进程」争用污染（step750–1000 掉到 ~578）；干净稳态 ≈1430–1450 img/s，实则仅次于 OpenVision2。四者最终 loss 全部 6.7342（同种子同数据同 text tower，SigLIP 对比平台）。

## S2 推理基准（batch=1 前向，bf16，224/16）

| 架构 | 参数量 | ms/img | image/s | token/s(=img×196) | 备注 |
|:---|:---|:---|:---|:---|:---|
| OpenVision2 | 505.0M | 6.508 | **153.7** | 30117 | 纯 Attention，最优 |
| DeepEncoderV2 | 516.9M | 17.761 | 56.3 | 11035 | 混合 AAMM，双向 Mamba 前向重 |
| MoE-ViE | 505.2M(222M) | 141.721 | 7.1 | 1383 | 路由+sort/grouped 纯 PyTorch，CPU 主导 |
| MambaEye | 534.9M | — | 卡死/超时 | — | mamba_ssm selective_scan 在 batch=1 停摆（150s 超时） |

> S2 说明：batch=1 单图推理是 MLLM 编码器最常见场景。SSM/MoE 的小 batch 延迟劣势在推理端被放大——MambaEye 全 SSM 在 batch=1 停摆、DeepEncoderV2 混合比纯 Attention 慢 ~2.7×、MoE-ViE 慢 ~22×（路由 CPU 开销）。纯 Attention 无论训练吞吐还是推理延迟均为最优。

## S3 长地平线（5000–10000 步 × 4 架构，en500k，cosine 跨度=steps）

| 架构 | 步骤 | 最终loss | loss@500 | loss@1000 | loss@5000 | 稳态img/s | GPU·h |
|:---|:---|:---|:---|:---|:---|:---|:---|
| OpenVision2 | 10000 | **4.4540** | 6.8542 | 5.9180 | 4.4560 | **2139.5** | ~2.35 |
| DeepEncoderV2 | 5000 | 4.4662 | 6.8541 | 5.9277 | 4.4662 | 1458.7 | ~1.61 |
| MambaEye | 5000 | 4.4700 | 6.8541 | 5.9463 | 4.4700 | 790.0 | ~2.56 |
| MoE-ViE | 5000 | 4.4661 | 6.8541 | 5.9406 | 4.4661 | 852.3 | ~2.10 |

> **S3 结论**：长地平线 loss 从 S1 的 6.7342 平台继续跌破至 ~4.45–4.47，**四架构 loss 差 <0.02（噪声级）**，架构在 loss 上不可区分。loss 排名（OpenVision2 4.454 < MoE-ViE 4.466 ≈ DeepEncoderV2 4.466 < MambaEye 4.470）无统计意义（< 多种子方差）。**决定性维度是吞吐/延迟**：OpenVision2 训练 2139 img/s（比 DeepEncoderV2 快 1.47×、比 MambaEye/MoE 快 2.5×）、推理 6.51ms（比 DeepEncoderV2 快 2.7×）。故锁定 **OpenVision2 为胜出架构 + 默认配置锚点（224/16、SigLIP、lr=1e-3、warmup100+cosine、seed1234、bf16、batch32×6）**。

## S4 多种子（top-2 架构 × 3 seed × 3000 步）

| 架构·seed | 最终loss | 训练img/s（稳态） |
|:---|:---|:---|
| openvision2_s1234 | 4.9962 | 1582.1 |
| openvision2_s42 | 4.9962 | 1636.7 |
| openvision2_s7 | 4.9962 | 1805.8 |
| deepencoder_v2_s1234 | 4.9962 | 1435.9 |
| deepencoder_v2_s42 | 4.9962 | 1437.7 |
| deepencoder_v2_s7 | 4.9962 | 1439.9 |

> **多 seed 结论**：6 run 最终 loss 全 4.9962（4 位完全一致）= cosine LR 3000 步尾部的 min_lr 平台，loss 与 seed/架构无关（seed 方差≈0）。**吞吐跨 seed 稳定且与架构绑定**（OV2 1582–1806 vs DE 1436–1440，稳定 1.1–1.25× 差距）→ 架构区分完全取决于吞吐。

## S5 下游代理检索（text↔image R@1/5/10，held-out laioncn/EN 5k，full ckpt）

| 架构 | t2i R@1/5/10 | i2t R@1/5/10 |
|:---|:---|:---|
| openvision2 | 0.0000 / 0.0012 / 0.0020 | 0.0000 / 0.0008 / 0.0020 |
| deepencoder_v2 | 0.0002 / 0.0010 / 0.0020 | 0.0002 / 0.0008 / 0.0016 |

> 3000 步随机 init 的 zero-shot 检索近乎随机（<1/5000），两架构并列无区分。无 ImageNet 类标签故 top-1/linear-probe 不可做（报告注明）。

## S6 分辨率/patch 消融（OpenVision2，3000 步，锚点 lr=1e-3）

| res/patch | 最终loss | 训练img/s |
|:---|:---|:---|
| 224/16（锚点） | 4.9962 | 1582.1 |
| 336/16 | 4.9962 | 1630.1 |
| 448/16 | 4.9962 | 960.4 |
| 224/14 | 4.9962 | 1613.8 |
| 336/14 | 4.9962 | 1289.7 |
| 448/14 | 4.9962 | 757.3 |

> loss 全 4.9962 = 锚点 lr=1e-3 塌到 min_lr 的平台（非分辨率/patch 差异）；有信息量的是吞吐——**token 数越多训练越慢**（224/16 1582 → 448/14 757 img/s）。

## S7 目标函数（SigLIP vs CLIP InfoNCE，OpenVision2，3000 步）

| 目标 | 最终loss | 训练img/s |
|:---|:---|:---|
| SigLIP（锚点） | 4.9962 | 1664.9 |
| CLIP InfoNCE | 2.8941 | 1717.5 |

> CLIP InfoNCE loss 尺度不同（softmax vs sigmoid），不可直接比；SigLIP 锚点 loss 仍受 lr=1e-3 平台限制。

## S8 LR 扫描（OpenVision2，3000 步）

| lr | 最终loss | 训练img/s |
|:---|:---|:---|
| 1e-3（锚点） | 4.9962 | 1651.3 |
| 3e-3 | 4.4562 | 1645.1 |
| 5e-3 | 4.4542 | 1615.8 |

> 🔑 **关键 LR 结论**：lr=1e-3 在 3000 步 cosine 尾部塌到 min_lr(1e-5)，末端 loss 停 4.9962；3e-3/5e-3 在相同步数仍维持有效学习率 → 收敛到更低 loss 4.4562/4.4542。即 **4.9962 平台 = lr=1e-3 的 LR 塌缩伪影，非数据/架构天花板**。生产建议 lr=3e-3。

## S9 推理深挖（OpenVision2，统一前向 bench batch∈{1,8,32}+多分辨率）

| 配置 | ms/img | image/s | token/s |
|:---|:---|:---|:---|
| batch=1 res=224 patch=16 | 10.069 | 99.3 | 19465 |
| batch=8 res=224 patch=16 | 0.887 | 1127.7 | 221029 |
| batch=32 res=224 patch=16 | 0.711 | 1405.7 | 275516 |
| batch=1 res=336 patch=16 | 7.118 | 140.5 | 61955 |
| batch=1 res=448 patch=16 | 6.949 | 143.9 | 112827 |
| batch=1 res=224 patch=14 | 10.206 | 98.0 | 25083 |

> batch 越大吞吐越高（batch=32 达 1406 img/s，接近训练吞吐），token/s 随 patch 数增加而增加（多分辨率需插值 pos-emb）。SGLang 未装，退化为统一前向 bench（见决策 4）。

## converged（最终汇总）

**胜出架构：OpenVision2（纯 Attention ViT，505.0M）** —— loss 四架构并列（~4.45–4.47），训练吞吐 2139 img/s（最快）与推理延迟 6.51ms（最快）双决定性优势。

**完整可复现训练命令**（详见 HTML 报告「可复现训练命令」节）：

```bash
conda activate py310
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027/run/vision

# 胜出架构完整训练（OpenVision2，默认配置锚点，6 卡 DP6）
bash run_train.sh openvision2 10000 out/S3_openvision2 \
    --data '/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar' \
    --batch-size 32 --seed 1234 --loss siglip

# 四架构长地平线（S3：OpenVision2 10k + 其余 3×5k）
bash run_s3.sh
# S4 多种子 / S6 分辨率patch / S7 目标 / S8 LR / S9 推理深挖
bash run_s4.sh  # top-2 × 3 seed × 3000
bash run_s6.sh  # cls∈{336,448} patch∈{14,16}
bash run_s7.sh  # siglip vs clip
bash run_s8.sh  # lr∈{1e-3,3e-3,5e-3}
bash run_s9.sh  # batch + 多分辨率 bench
```

**产物**：`doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html`（自包含，已回填）+ `ISEDA2027/6_vision_encoder.tex`（config/results 已回填）。

**裁剪说明（预算）**：S7 数据侧（caption 粒度·规模·中英比例）因重 prep + 低信息量裁剪；S9 的 SGLang 生产栈未装（推迟到 MLLM Stage iv）。详见 HTML「局限」节。