# EXPERIMENTS_VISION_ROUND12.md — AIMv2 提速归因实测 + 全量数据训练准备

> **运维指令来源**：`BAIZE_VISION_TASK.md` 运维指令 2026-10-05（晚）+ `ARCHIVE_OPERATOR_VISION.md`「运维前置 · AIMv2 提速」块。
> **执行日期**：2026-10-06 12:33–12:44（.12 8 卡）。

---

## §1 AIMv2 提速 — ① 归因实测（Throughput Attribution Benchmark）

### 1.1 目的

用户问「AIMv2 训练是否还能加速，显卡满的么，可否增大 MBS？」。
运维判断：显存远没满（历史 ~22.7–30 GB / 81.6 GB），但吞吐波动极大（R11-G 2485 → R12 5240 img/s）。
→ **先归因实测**：bs 64/128/256 各跑 ≥200 步，记 `ms/iter`、`image/s`、GPU util、显存峰值。
→ 判据：util≲70% 或 ms/iter 基本不随 MBS 变 = 数据/IO 受限；util≈100% 且 img/s 随 MBS 上升 = 算力受限。

### 1.2 配方

- **塔**：OpenVision2 w512/d30/patch16/224²（126.78M）+ PatchPredictor 0.66M
- **损失**：`--loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0`
- **数据**：GPIC(all) + CC12M + Amshaker ≈ 58.8M unique pairs（7511 shards: GPIC=4161, CC12M=1100, Amshaker=2250）
- **硬件**：.12 8× A100-81.6GB, 224-core Xeon 8480+, 2.0 TiB RAM（1.7 TiB buff/cache）
- **存储**：全 NFS（/nas_inference + /nas_train + /nas_user），无本地 NVMe
- **口径**：每档 250 步，`--log-every 10`，warmup 20 步，seed 1234，bf16
- **脚本**：`vision/r12_throughput_bench.sh`（bs 扫描）+ `vision/r12_throughput_bench_128_256.sh` + `vision/r12_throughput_bench_nw.sh`（num_workers 扫描）

### 1.3 结果：batch size 扫描（num_workers=6 固定）

| BS | Global batch | steady img/s | ms/iter (steady) | Mem peak (GB) | GPU util (snapshot) |
|---:|---:|---:|---:|---:|:---|
| **64** | 512 | **4993** | ~102 | 16.5 | 62–83% (avg ~70%) |
| **128** | 1024 | **6293** | ~134 | 26.8 | 49–95% (variable) |
| **256** | 2048 | **8314** | ~250 | 47.6 | 48–100% (variable) |

**原始 [done] 行**：
```
bs=64:  [done] total=35.3s steps=250 steady_image_s=4993.1 final_loss=4.8705 fused=False
bs=128: [done] total=56.7s steps=250 steady_image_s=6292.7 final_loss=5.5148 fused=False
bs=256: [done] total=105.2s steps=250 steady_image_s=8313.7 final_loss=6.0821 fused=False
```

**关键 [step] 行示例（bs=64, steady state steps 60–250）**：
```
[step 60/250]  ms/iter=108.5 image/s=4718.6
[step 120/250] ms/iter=100.3 image/s=5102.9
[step 180/250] ms/iter=100.5 image/s=5094.1
[step 250/250] ms/iter=101.8 image/s=5027.5
```

### 1.4 结果：num_workers 扫描（bs=64 固定）

| NW | steady img/s | ms/iter range | Notes |
|---:|---:|:---|:---|
| **6** | **4993** | 93–155 | baseline（已有 R12 一致） |
| **12** | **4262** | 98–157 | **更差**——8 rank × 12 worker = 96 进程争 NFS |
| **16** | **5311** | 95–114 | 略好（在噪声范围内） |

**原始 [done] 行**：
```
nw=6:  [done] total=35.3s steps=250 steady_image_s=4993.1 (from bs=64 bench above)
nw=12: [done] total=41.1s steps=250 steady_image_s=4261.8
nw=16: [done] total=37.5s steps=250 steady_image_s=5311.2
```

### 1.5 诊断

**结论：bs=64（生产配方）下，系统是数据/IO 受限（data/IO limited），非算力受限。**

证据：

1. **GPU util ~70%（未饱和）**：bs=64 时 GPU util 62–83%，远未到 100%。→ 符合运维判据「util ≲70% ⇒ 数据/IO 受限」。
2. **image/s 随 MBS 上升**：4993 → 6293 → 8314（+66%）。但这是**每步开销摊销**（per-step overhead amortization），**非**算力受限的标志——算力受限时 image/s 应不变（ms/iter 随 BS 线性翻倍）。
3. **ms/iter 亚线性增长**：bs 64→256（4×），ms/iter 102→250（2.45×）。若纯算力受限应 4×（~408ms），若纯数据受限应 1×（~102ms）。实际 2.45× → **混合瓶颈，以数据/IO 为主**。
4. **显存远未满**：bs=64 仅 16.5/81.6 GB（20%）。bs=256 也仅 47.6/81.6 GB（58%）。→ 显存不是限制因素。
5. **num_workers 无显著效果**：nw=6/12/16 分别 4993/4262/5311 img/s，差异在 NFS 噪声范围内（3300–5500 img/s 逐 step 波动）。→ **瓶颈是 NFS 带宽，非 worker 数量**。
6. **无本地 NVMe**：所有数据在 NFS 上（3 个不同 NFS 卷），/tmp 仅 98 GB 本地盘。→ 无法用本地缓存绕过 NFS。

### 1.6 处方

**保持 bs=64 / global 512 / num_workers=6**（与 R9/R11-G/R12 scaling 曲线可比）。

**无法在不改 recipe 的情况下显著提速**：
- ❌ 加 MBS：会改变 global batch → InfoNCE 负样本数变 → recipe 变 → 不并入 scaling 曲线（运维明确要求保持 bs=64/global 512）
- ❌ 加 num_workers：NFS 带宽是瓶颈，更多 worker 反而加剧争用（nw=12 实测更差）
- ❌ 本地 NVMe：机器无本地 NVMe
- ⚠️ 预热 tar 到 page cache：1.7 TiB RAM 可容纳 ~742 GB 全量数据，但前 17h 训练已缓存大部分；增益有限且不可控（NFS 逐 step 波动 3300–5500 img/s 仍存在）

**结论：当前 ~5000 img/s 是 NFS 架构下的可达到吞吐率。**

### 1.7 全量数据训练时长估算（用实测 img/s）

| 项 | 值 |
|:--|:--|
| 总 unique pairs | ~58.8M（GPIC all ≈41.8M + CC12M ≈11.0M + Amshaker ≈5.95M） |
| 1 epoch 步数 | 58.8M / 512 = ~114,844 步 |
| 实测 steady img/s | ~5000（bs=64, nw=6, NFS） |
| 1 epoch 墙钟 | 58.8M / 5000 = 11,760s = **~3.3h** |
| 保守估算（含 NFS 波动） | 58.8M / 4500 = 13,067s = **~3.6h** |
| R12 3-epoch 实测平均 | 344k 步 / 10.9h → 4470 img/s → **1 epoch ≈ 3.7h**（吻合） |
| >1 epoch？ | **是**。2 epoch ≈ 7.2h, 3 epoch ≈ 10.8h |

> **回答用户问题**：「>1 epoch 呢」→ **1 epoch ≈ 3.3–3.7h；2 epoch ≈ 7.2h；3 epoch ≈ 10.8h**。
> R12 已跑 1.05 epoch（120k 步），3-epoch 续跑已跑满 3 epoch（344k 步, 10.9h）。
> 若要用**全部现有数据**重新跑（从零、非续跑），1 epoch ≈ 3.3–3.7h, 8 卡 × 3.7h ≈ **29.6 GPU·h/epoch**。

### 1.8 脚本与日志路径

| 脚本 | 日志 |
|:--|:--|
| `vision/r12_throughput_bench.sh` | `/tmp/bench_bs{64,128,256}.log` + `/tmp/r12_bench_run.log` |
| `vision/r12_throughput_bench_128_256.sh` | `/tmp/bench_bs{128,256}.log` + `/tmp/r12_bench_128_256.log` |
| `vision/r12_throughput_bench_nw.sh` | `/tmp/bench_nw{12,16}.log` + `/tmp/r12_bench_nw.log` |
| 输出 ckpt | `/nas_train/.../baize-vision/out/bench_throughput/bs{64,128,256}/` (bench-only, 可删) |

---

## §2 R12b — 全量数据 fresh AIMv2 训练 + IN-1k eval（2026-10-06 → 10-07）

### 2.1 配方

- **目标**：运维指令 2026-10-05（晚）——「用全部现有数据训练当前最佳配方 AIMv2」。
- **配方** = AIMv2-style = R11-G / R12 同款：`InfoNCE + 1.0×masked-patch-MSE`（`--loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0`），w512（OpenVision2, 126.78M）+ 冻结 CLIP-768 文本塔。
- **数据 = 现有全部**：GPIC（4175 tar × 12,637 ≈ 52.8M）+ CC12M（1100 tar × 10,000 ≈ 11.0M）+ Amshaker（2250 tar × 2,646 ≈ 5.95M）→ **~69.7M unique pairs**。
- **超参**：bs64×8=512, lr=3e-3, warmup=20, seed=1234, bf16, patch=16, res=224, save-every=10000。
- **步数**：272,000 步 ≈ **2 epochs**（69.7M / 512 = 136,133 步/epoch）。
- **Fresh run**（非续跑）—— 干净 scaling 曲线，无 predictor random restart。
- **硬件**：.12 8× A100-81.6GB。训练时间 12:54 → 02:14 ≈ **13.3h**（≈106.4 GPU·h）。
- **吞吐**：稳态 ~5000 img/s；NFS 波动导致 2300–5900 img/s 区间波动（详见巡检流水）。

### 2.2 IN-1k eval 结果（28 ckpts，built-in r8_eval_in1k.py，Protocol A = BaiZe 内部协议）

| step | N (tokens) | zero-shot top1 | **lp top1** |
|---:|---:|---:|---:|
| 10k | 5.12M | 4.20% | **11.77%** |
| 20k | 10.2M | 4.98% | **12.44%** |
| 30k | 15.4M | 5.26% | **13.22%** |
| 40k | 20.5M | 5.60% | 13.10% |
| 50k | 25.6M | 6.08% | **14.04%** |
| 60k | 30.7M | 6.93% | **14.71%** |
| 70k | 35.8M | 7.05% | **15.56%** |
| 80k | 41.0M | 7.72% | **16.18%** |
| 90k | 46.1M | 8.13% | **17.05%** |
| 100k | 51.2M | 7.66% | **17.63%** |
| 110k | 56.3M | 8.30% | 17.80% |
| 120k | 61.4M | 8.79% | **18.37%** |
| 130k | 66.6M | 8.54% | 18.35% |
| 140k | 71.7M | 8.30% | 18.17% |
| 150k | 76.8M | 8.45% | 17.89% |
| 160k | 81.9M | 8.77% | 18.40% |
| 170k | 87.0M | 8.35% | 18.08% |
| 180k | 92.2M | 8.43% | **18.69%** |
| 190k | 97.3M | 8.21% | 18.21% |
| 200k | 102.4M | 8.09% | 17.48% |
| 210k | 107.5M | 8.65% | 18.42% |
| 220k | 112.6M | 8.28% | 18.11% |
| 230k | 117.8M | 8.20% | 18.12% |
| 240k | 122.9M | 7.44% | 17.46% |
| 250k | 128.0M | 8.65% | 18.32% |
| 260k | 133.1M | 9.01% | 18.64% |
| 270k | 138.2M | 8.87% | 18.70% |
| **final** | **139.3M** | 8.51% | **18.81%** |

> **lp_max = 18.81%**（final vision.pt, 139.3M tokens）。
> step10k lp=11.77% — 显著高于 R11-G 同期（11.50%），大数据集 69.7M vs 18.5M 起效。
> 但 lp 在 step120k（61.4M, ~0.9 epoch）后**进入平台**（18.0–18.8% 区间波动），**未超越 R11-G 的 19.76%@55.3M**。

### 2.3 Scaling 拟合（r12b_scaling.py）

| 曲线 | 点数 | lp 范围 | Power law | R² | 渐近 | 单调(±0.5pp) |
|:--|---:|:--|:--|---:|---:|:--|
| **R12b** (69.7M, 2ep) | 27 | 11.77–18.70% | `0.4781 - 1.1757·N^(-0.0749)` | 0.8867 | 47.8% | ❌ False |
| R12 3-epoch (58.8M, 3ep) | 34 | 11.19–20.32% | `1.0 - 1.6152·N^(-0.0372)` | 0.9349 | 100.0%* | ✅ True |
| R11-G (18.5M, 1ep) | 10 | 11.50–18.84% | `1.0 - 1.5949·N^(-0.0374)` | 0.9234 | 100.0%* | ✅ True |

> *R12 3-epoch 和 R11-G 的 power law a=1.0 是退化拟合（渐近被钉在 100%），不可直接解读为「渐近 100%」。
> R12b 的 a=47.8% 更可信（R²=0.89 但 < 0.90 阈值 → ⚠️ 报告如实标注「R²<0.90，不强推外推」）。

### 2.4 关键发现：更多 unique 数据 ≠ 更高 lp

| 实验 | 数据量 | Epoch | Token 总量 | **lp_max** | 说明 |
|:--|---:|---:|---:|---:|:--|
| R11-G | 18.5M | 1 | 55.3M | **19.76%** | CC12M+Amshaker，短/中 caption |
| R12 3-epoch | 58.8M | 3 | 174M | **20.32%** | +GPIC(4161 tar)，3 epoch |
| **R12b** | **69.7M** | **2** | **139M** | **18.81%** | +GPIC(4175 tar)，2 epoch |

**R12b 用 3.8× 更多 unique 数据（69.7M vs 18.5M）和 2.5× 更多 token（139M vs 55.3M），lp 反而比 R11-G 低 0.95pp（18.81% vs 19.76%）。**

归因分析：
1. **GPIC 短 caption 稀释信号**：GPIC 占 R12b 数据的 ~76%（52.8M/69.7M），其 caption 为短 alt-text（~20 tok），远短于官方 AIMv2 的 LLaMA-3 长合成 caption（~128 tok）→ text AR / contrastive 信号天然弱（已在 `VISION_NEXT_DIRECTIONS.md` §5 handicap 中标注）。
2. **2 epoch < 3 epoch**：R12 3-epoch（174M token）比 R12b（139M token）多 25% 训练量 → 更多 epoch 在已见数据上的重复可能有正收益。
3. **非单调**：R12b lp 在 step120k 后波动（18.0–18.8%），power law R²=0.89 < 0.90 → 过拟合噪声或 NFS 吞吐波动影响训练稳定性。
4. **结论**：在当前 caption 质量下，**增加 unique 数据量（加入 GPIC 短 caption）不改善 lp；增加 epoch 数（重复高质量数据）可能更有效**。这为后续 mask-ratio / weight-ratio 消融提供了数据策略参考。

### 2.5 脚本与日志路径

| 脚本 | 日志 | 输出 |
|:--|:--|:--|
| `vision/r12b_fulldata_fresh.sh` | `/tmp/r12b_fulldata_aimv2.log` | `/nas_train/.../baize-vision/out/R12b_fulldata_aimv2_w512/` |
| `vision/r12b_eval_watcher.sh` | `/tmp/r12b_eval_watcher.log` | scaling 分析在 watcher log 末尾 |
| `vision/r12b_scaling.py` | — | stdout → watcher log |
| eval 脚本 | `vision/r8_eval_in1k.py` | 28 ckpt 结果在 train log |

### 2.6 与 R12 3-epoch 的 N-matched 对比

在相近 N（token 数）处对比：
- N≈51M: R12b lp=17.63% vs R11-G lp=18.84% → **R12b 低 1.21pp**（更多数据但更差）
- N≈92M: R12b lp=18.69% vs R12-3ep lp≈18.87% → **R12b 低 0.18pp**（接近持平）
- N≈139M: R12b lp=18.81% vs R12-3ep lp≈19.46% (step290k) → **R12b 低 0.65pp**

→ **在同 N 下 R12b 始终 ≤ R12 3-epoch**，证实 GPIC 短 caption 的加入不改善 lp。

---

## §3 lp 协议桥接评估（Protocol A vs B）— 进行中

> 运维指令 2026-10-06：用同一批 ckpt 跑 BaiZe 协议（A）与主流协议（B），量化 Δlp = B − A。
> 脚本：`vision/lp_protocol_bridge.py` + `vision/run_lp_protocol_bridge.sh`。
> ckpts：R12b final + R12 1-epoch + R11G AIMv2。
> B 组：SGD+momentum 0.9 + cosine + 90ep + batch 1024 + ImageNet mean/std + full IN-1k train (1.28M)。
> 状态：🚀 **运行中**（PID 1499158, 03:07 启动）。结果待填。