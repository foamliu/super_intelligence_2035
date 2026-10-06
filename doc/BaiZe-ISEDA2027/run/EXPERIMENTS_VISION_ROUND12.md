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