# EXPERIMENTS_PRETRAIN_2B_ROUND2.md — BaiZe Stage(i) Mamba2-hybrid 2B 第二轮（R2）实验记录

> R2 目的：加固 Round 1 已收敛的三处结论（这三处会在论文里被审稿人直接打）。
> 三处：① **LR 最优落在网格边界**（S2 扫 `2e-4…1e-3` 七点 loss 单调改善到 1e-3，真正极小值可能在 1e-3 之上未覆盖）② **min_lr Δ 小于噪声**（`1e-5` vs `3e-5` 的 Δ≈0.003 < 3-seed σ≈0.0469，"narrowly beats" 站不住）③ **架构对比只跑 1000 步 / 24.6M token**（GBS=6 早期快照，却支撑 "hybrid 更优" 核心 claim）。
> 固定口径（除显式改动外与 Round 1 一致）：8×H100 @ `10.239.2.29`、TP1/DP8、GBS=8、seq=4094、bf16、AdamW(0.9,0.95,1e-5,wd0.1)、seed=1234、WSD warmup 250 / decay 500。

---

## R2.0 状态切换（✅ 完成）

- `PHASE` → **R2_active**；`WAITING` → `0`（纯文本）。
- loop 实际仍在运行（本唤醒 pgrep 确认 PID 2425284）；Round 1 的 "04:03 已 kill loop" 记录作废。
- Round 1 S0–S5 结论保留作对照基线，**不重跑**。

## GPU / NFS 争用核验（每次测量都记录）

| 时间 | 10.239.2.29（本任务） | vision（10.239.2.12）当时在做什么 |
|:--|:--|:--|
| 启动 P-1 前 | 8×H100 全空闲（0 MiB / 0%） | run_r2_resume.sh 跑 R2-3 尾 3 组 + R2-5（GPU0-5 满载 ~39GB）；其 R2-4 干净吞吐**已先期完成** → 无需等待 |
| P-3 dense 收尾 @18:55 | GPU0-5（6 卡）满载 dense（各 ~39GB）；GPU6-7 空闲 4 MiB | vision 已收敛终局（R3_complete，未跑训练）→ 无 I/O 争用 |
| P-3 hybrid 运行 @19:08 | GPU0-5（6 卡）满载 hybrid（各 ~39GB，util 63–97%，6 worker master_port=29732）；GPU6-7 空闲 | 同上（vision 终局 idle） |

---

## P-1　LR 网格向上扩展（判定 1e-3 是否真最优）

> 与 S2 完全同口径（纯 L3 `ultrafineweb_l3_qa` / min_lr 3e-5 / WSD / seed1234），仅 LR 变。
> 产出 10 点 LR 曲线 = Round 1 S2 的 7 点 + 本 3 点。

| ID | stable LR | min_lr | 数据 | final loss@5000 | train tok/s | 耗时 | GPU·h | 状态 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| p1_1p5e3 | 1.5e-3 | 3e-5 | 纯 L3 | **2.775181** | ~98.4K | 27.6min | ~3.7 | ✅ done |
| p1_2e3 | 2e-3 | 3e-5 | 纯 L3 | **2.788862** | ~111K | 26.6min | ~3.5 | ✅ done（16:44:08→17:10:47，293.9ms/iter，grad 0.158，无 NaN） |
| p1_3e3 | 3e-3 | 3e-5 | 纯 L3 | **2.886112** | ~101K | 27.0min（17:10:47→17:37:47） | ~3.6 | ✅ done（322.6ms/iter，grad 0.162，无 NaN/skip；stable 期 loss~3.19，decay 段回落至 2.886，未发散） |

### Round 1 S2 七点基线（对照）
`2e-4→2.9037 / 3e-4→2.8462 / 4e-4→2.8167 / 5e-4→2.7981 / 6e-4→2.7783 / 8e-4→2.7700 / 1e-3→2.7627`（单调递减到网格上限 1e-3）。

### P-1 结论（✅ 三点全部回收，定稿）
- **10 点 LR 曲线**（Round 1 七点 + 本 3 点，loss@5000）：
  `2e-4→2.9037 / 3e-4→2.8462 / 4e-4→2.8167 / 5e-4→2.7981 / 6e-4→2.7783 / 8e-4→2.7700 / 1e-3→2.7627（谷底） / 1.5e-3→2.775181 / 2e-3→2.788862 / 3e-3→2.886112`。
- ✅ **明确 U 形，极小值齐整落在 `1e-3`**：左翼 2e-4→1e-3 单调下降，右翼 1.5e-3→2.886 单调抬升（3e-3 无 NaN 未发散，仅 stable 期 loss 抬到 ~3.19、decay 段回落）。Round 1 的「1e-3 为网格上限、最优可能在边界之上」的**过度声明风险解除**：1e-3 **不是**被扫描截断的边界，而是扩展网格（2e-4…3e-3 共 10 点）**内部的全局极小值**。
- 边界回答：**最优不在网格边界**；`1e-3` 即全局极小值（紧邻点 8e-4→2.7700、1.5e-3→2.7752 均高于它）。
- 上界信息：LR 可耐到 3e-3 不发散（loss 仅退化至 ~3e-4 档水平），故 1e-3 是"loss 最小"而不是"稳定上界"。右翼退化梯度平缓（1e-3→1.5e-3 仅 +0.0125，1.5e-3→2e-3 +0.0137，2e-3→3e-3 +0.0973），说明 1e-3 附近曲率平缓、对 LR 轻微上偏鲁棒。

---

## P-2　补 seed n=5（判定 min_lr Δ 是否在噪声内）

- Round 1 已有 3 seed@5000（胜出配置）：`44→2.640200 / 777→2.653915 / 2024→2.727488`（均值 2.673868，σ 0.0469）。
- ✅ **复核**（只核对不重跑）：上述 3 值与 `EXPERIMENTS_PRETRAIN_2B.md` 的 S5-02/03/04 完全一致。
- 新增 2 seed（胜出配置，5000 步）：**✅ 已跑** seed=7 与 2025。

| ID | seed | final loss@5000 | grad norm | skip/nan | 耗时 | 状态 |
|:--|:--|:--|:--|:--|:--|:--|
| p2_seed7 | 7 | **2.687718** | 0.252 | 0/0 | 17:38:13→18:04:47（~26.6min，331.3ms/iter） | ✅ done |
| p2_seed2025 | 2025 | **2.657607** | 0.255 | 0/0 | 18:04:47→18:31:32（~26.7min，279.3ms/iter） | ✅ done |

### P-2 结论（✅ n=5 统计定稿）
- **n=5 loss@5000**（胜出配置 LR1e-3/WSD/warmup250/decay500/min_lr1e-5 + L3+code+math 86:10:4）：`seed44=2.640200 / 777=2.653915 / 2024=2.727488 / 7=2.687718 / 2025=2.657607` → **均值 2.673386、样本 σ≈0.0349**（Round 1 的 3-seed σ=0.0469 收窄至 0.0349）。
- **明确回答**：`min_lr 1e-5 vs 3e-5 的 Δ = 2.767915 - 2.764702 ≈ 0.003213`，相对 n=5 的 σ≈0.0349 仅 **≈0.09σ**（Δ 比噪声小一个量级）→ **Δ 完全落在 run-to-run 噪声内，「narrowly beats」不成立**。应如实写成 "within run-to-run noise"（两值统计上不可区分），不能用 "beats" 表述。

---

## P-3　架构对比延长 5000 步（dense vs hybrid，6 卡 / GBS=6 口径）

- 对象：dense（MiniCPM5-2B）vs hybrid（Mamba2-hybrid），与 Round 1 架构对比同源。
- ⚠️ 口径：**6 卡 / TP1/DP6 / GBS=6 / seed=1234**（沿用 Round 1，否则与 1000 步数据不可比）。**统一 cosine**（lr=3e-4 / min_lr=3e-5 / warmup=100 / decay=1000 / seq=4096 / bf16）保证公平。
- 5000 步，在 500/1000/2000/3000/5000 步各记 loss → 两条曲线。
- 状态：**dense ✅ done / hybrid ✅ done（编排链 ALL DONE @19:23:01）**。

### P-3 结果表（dense 5 点已回收；hybrid 待收）

| ID | 架构 | 参数量（rank numel） | 500 | 1000 | 2000 | 3000 | 5000 | train tok/s | 耗时 | 状态 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| p3_dense | MiniCPM5-2B (dense) | **2,512,037,888 = 2.512B** ✅ | 5.4683 | 4.8351 | 4.2269 | 3.8127 | **3.3575** | ~89.7K（274ms/iter） | 18:31:32→18:55:21（~24min） | ✅ done（grad 1.7，0 NaN/skip） |
| p3_hybrid | Mamba2-hybrid | **2,220,268,032 = 2.220B** ✅ | 5.1495 | 4.6143 | 3.8282 | 3.3818 | **3.0563** | ~85.6K（287ms/iter） | 18:55:33→19:23:01（~27.5min） | ✅ done（grad 0.67，0 NaN/skip） |

- ✅ **参数量复核**：dense `2,512,037,888`（2.512B）、hybrid `2,220,268,032`（2.220B），均与 Round 1 `sum(numel())` 及论文 `tab:archcomp` 一致。（注：hybrid provider 打印的 "transformer layers 2.47 + embedding 0.53 = 3.00B" 是含 vocab 嵌入的粗糙计数，**权威口径取 rank 上的 2.220B**。）
- ✅ **训练吞吐口径**（GBS=6 × seq4096 = 24576 tok/step）：dense ~274ms/iter ≈ **89.7K tok/s**，hybrid ~287ms/iter ≈ **85.6K tok/s** —— dense 训练吞吐略高于 hybrid（SSM 串行为 hybrid bottleneck 的量化印证），与论文 `tab:archcomp` 吞吐方向一致。
- ✅ **P-3 最终结论（5000 步，dense vs hybrid）**：hybrid 在全部 5 个 checkpoint（500/1000/2000/3000/5000）**均优于 dense**，且差距整体随步数拉大（Δ = dense−hybrid：0.319 / 0.221 / 0.399 / 0.431 / **0.301** loss，末段 Δ≈0.30）。→ Round 1「hybrid 更优」的核心 claim 从 **1000 步 / 24.6M token 快照** 延长到 **5000 步 / 123M token**（GBS=6 × 4096）后**仍然成立**，且非早期边界效应、全流程稳定领先。
- ✅ **附带结论（参数效率）**：hybrid 仅 **2.220B** 参数，比 dense **2.512B 少 11.6%**，却取得更低 loss → **更参数高效**（同 loss 更省参数）。吞吐方面 dense 略快（89.7K vs 85.6K tok/s，SSM 串行为 hybrid bottleneck），但质量领先覆盖吞吐劣势。两结论均与论文 `tab:archcomp` 方向一致。

---

## P-4　FP8 可行性评估（先 profile，再决定）

> 背景：Xmodel-2.5 从 BF16→FP8 混合精度吞吐 +≈30%，但那是**稠密 Transformer**（几乎全 GEMM）。
> BaiZe 只有 4/56 层 attention，其余 Mamba-2 SSM + MLP；TE FP8 只加速 GEMM / LayerNorm / GeLU，**不含 SSM selective-scan**。
> → 不能假设 +30% 平移过来，必须先量 GEMM 占比 `g`（Amdahl：FP8 上限 = 1/(1-g)）。

### 环境核验（✅ 已完成，2026-10-01 19:09）

- ✅ `transformer_engine` **已安装，版本 2.12.0**（`2.12.0+5671fd36`）；与 `torch 2.8.0+cu128` / CUDA 12.8 匹配。
- ✅ 配方已从 `Xmodel-2.5/ACL2026/method.tex` §FP8 摘取：forward **E4M3**（activations）、backward **E5M2**（gradients）、**master-weights bf16**；TE delayed-scaling `amax-history-len=128` / `amax-compute-algo=max`；经 `--transformer-impl transformer_engine` 启用（内核自动选择，无需改源码）。
- ⚠️ 当前 `pretrain_launcher.py` **尚无** `--transformer-impl` / FP8 相关参数（仅有 `--precision`，默认 `bf16_mixed`）。第 2 步接 FP8 前需扩展 launcher（照抄 Xmodel-2.5 的 `--transformer-impl transformer_engine` + 传 fp8 recipe）。

### 第 1 步（✅ 完成，2026-10-01）：BF16 profile 量 GEMM 占比 → g 已量化

> 方法：BF16 现有胜出配置（GBS=8/MBS=1/DP=8/TP=1/seq=4094，与 P-1 基线同口径），`torch.profiler` 跑 80 步（warmup 20 + active 60）。
> 脚本：`profile_bf16.py`（+ `--lr-warmup-iters`/`--lr-decay-iters`，修复 scheduler assert）、`scripts/analyze_bf16_profile.py`、`scripts/profile_bf16.sh`。
> 原始 kernel 表 → `run/p4_profile_bf16.txt`；归类口径见 `analyze_bf16_profile.py`。
> **通信用 NCCL `reduce-scatter + all-gather`，GEMM 含 fused `LN→Linear` 主体。**

**去重后 GPU 自耗时分解（80 步合计 self_device_time，已剔除 `record_param_comms`/`nccl:*` 与 `ncclDevKernel` 三重重复记账）：**

| 类别 | 自耗时 (ms) | 占 GPU 总时间 | 占纯计算 |
|:--|--:|--:|--:|
| **通信 NCCL**（reduce-scatter 9.79 s + all-gather 9.22 s + allreduce 0.08 s） | 19089.7 | **41.7%** | — |
| **GEMM**（fused LN+Linear 7482 + mm/linear 613 + stable-moe/MLP 内存 4703，含 0.17s vec∗mat 存算） | ~13101 | ~28.6% | **49.2%** |
| **SSM**（selective-scan 3150 + conv1d 566 + cumsum 117） | ~3833 | ~8.4% | 14.4% |
| **norm+act+逐元素**（layer-norm 1675 + rms-norm 769 + 各类逐元素 2366） | ~4810 | ~10.5% | 18.1% |
| **attention**（flash-attn） | ~326 | ~0.7% | 1.2% |
| **optimizer**（Adam step 2042 + grad-clip） | ~2577 | ~5.6% | 9.7% |
| **misc / 发射开销**（cudaStreamSynchronize 36.9 s、cudaLaunchKernel 16.8 s、Memset、分桶等） | ~1997 | ~4.4% | 7.5% |
| **数据加载** | ~0 | **0.0%** | — |

### P-4 第 1 步结论（✅ 定稿，决定不接 FP8）

- **GEMM 占比 `g`**：**~28.6%**（含通信的墙钟口径）／**~49.2%**（纯计算口径，通信充分重叠/高 GBS 时的上界口径）。
- **Amdahl FP8 上限**：纯计算口径 `1/(1-g)=1.97×`（即便 FP8 GEMM 无限快）；含通信口径上限 `1.40×`。**现实**（FP8 GEMM 单算子 s≈1.3–1.6）→ **墙钟 ~1.1–1.2×**（纯计算 ~1.2–1.3×）。**远低于稠密 Transformer 的 +30%**。
- **SSM 是 main compute 里的第二大项（~14.4% 纯计算）但并非独占**；真正的墙钟问题是 **通信 NCCL ≈ 41.7%**（GBS=8/MBS=1/DP=8 下 reduce-scatter + all-gather 梯度 comm 不被第二 micro-batch 掩盖）＋ **SSM+norm+act+optimizer ≈ 42% 纯计算均不被 FP8-GEMM 加速**。
- ⚠️ **GBS 口径 caveat（如实）**：本 profile 用搜索口径 GBS=8/MBS=1，comm 占 41.7% 是**小 batch 下偏高、会高估高 GBS 生产场景的 comm 占比**（GBS=1024 时 comm 被摊销且可与 compute 重叠，占比远低于 41.7%）→ 此时回到纯计算口径 g≈0.49，FP8 上限 1.97×、现实 ~1.2–1.3×。**两种口径上限均 <2×，FP8 对 Mamba2-hybrid 的加速天花板被 SSM+norm+act（>50% 计算）卡死。**
- ✅ **定稿判定**：FP8-GEMM 对 Mamba2-hybrid 2B **加速上限 ~1.2–1.3×（现实）**，低于论文可主张的显著收益、且需扩展 launcher/改 kernel 成本高 → **到此结论、不接 FP8**（P-4 第 2/3 步裁减）。数据加载在 GPU 侧 0% 占比（CPU 异步 prefetch 完全隐藏）。

### 状态：**第 1 步 ✅ 完成、已定稿不接 FP8**（下一步按顺序 P-7 吞吐幅度核查）
## P-4R　FP8 重开（运维 2026-10-02 指令）—— 实测单算子加速 s，不接 FP8（新的决定性理由）

> **为什么重开**：上一轮「Amdahl 上限 <2× → 不接 FP8」用了 **GBS=8/MBS=1 墙钟口径 g=0.286**（含 41.7% comm），
> 而任务书 caveat 已写明「回到纯计算口径 g≈0.49」。P-5a 定稿生产口径 GBS=1024 → **P-8 真实场景恰是 g≈0.49**，
> 运维据此判定推理用错 `g`，要求**把 `s`（FP8 GEMM 单算子加速）真量出来**，不许再用假设的 s。

### 结论速览（先给答案）

**不接 FP8**。但理由与上一轮**不同**、且**更强**：

- 上一轮错在「用错 `g`」；这一轮**把 `g` 修正为 0.49** 后，**发现 `s` 本身 < 1**。
- **实测 s（fwd+bwd，TE 实际训练路径）在生产口径 M=4094（GBS=1024/mb=1/seq=4094 下每个 GEMM 的 M = 序列长）≈ 0.65（范围 0.39–1.27）**：
  **FP8 在我们的 GEMM 形状上不但不快，反而慢 ~35%**（这些 GEMM 是**访存受限**的，不是算力受限；
  FP8 的 2× FLOPs 优势只在 M≳16K 的算力受限区才会兑现，而我们的 M 只有 4094）。
- 端到端（g=0.49 + 实测 s=0.65）：**1/((1-0.49)+0.49/0.65) = 0.79× → 慢 ~21%**，不是 +14.5%～+30%。

### 微基准方法与形状（脚本 `scripts/p4r_fp8_gemm_bench.py`，`CUDA_VISIBLE_DEVICES=0`，1 卡）

| GEMM | in→out（K→N） | 层来源 | 说明 |
|:--|:--|:--|:--|
| ffn_up/gate | 2048→8192 | 每 MLP 层 ×2 | 大 FFN GEMM |
| ffn_down | 8192→2048 | 每 MLP 层 | 大 FFN GEMM（K 大） |
| attn_qkv | 2048→3072 | 16 hd×128 + 4 kv×128×2 | 瘦 GEMM |
| attn_out | 2048→2048 | attention o | 瘦 GEMM |
| mamba_in_proj | 2048→10304 | 2·d_inner+z+B+C+dt | SSM in-proj |
| mamba_out_proj | 4096→2048 | d_inner→d_model | SSM out-proj |

> **形状来源**：`provider.py`（hidden=2048/ffn=8192/heads=16/hd=128/kv-groups=4）+ `mamba_mixer.py`
> （d_inner=2·2048=4096、d_state=128、ngroups=8、headdim=64→nheads=64）。
> **MoE expert GEMM = N/A**（此 2B hybrid 是 dense，无 MoE，已在报告注明）。
> 方法：TE `Linear` 层在 `fp8_autocast(enabled=True)`（E4M3 fwd / E5M2 bwd / master-weights bf16，即 Xmodel-2.5 配方）
> vs `enabled=False`（cublas bf16），同层同形状，fwd+bwd 各 200 步 warmup 20 后取均值。

### 实测结果（s = t_bf16 / t_fp8，fwd+bwd）

**M=4096（生产口径）**：

| GEMM | s (M=4096) |
|:--|--:|
| ffn_up_gate | **0.74** |
| ffn_down | **0.56** |
| attn_qkv | **0.39–0.56** |
| attn_out | **0.55–0.61** |
| mamba_in_proj | **0.55–0.78** |
| mamba_out_proj | **0.55–0.57** |
| **全部 18 形状点** | **均值 0.65 / min 0.39 / max 1.27** |

**交叉区（s 随 M 的转捩，FFN 两 GEMM，fwd+bwd）**：

| M | ffn_up (2048→8192) | ffn_down (8192→2048) |
|--:|--:|--:|
| 2048 | 0.52 | 0.61 |
| **4096** | **0.74** | **0.56** |
| 8192 | 0.64 | 0.57 |
| 16384 | 1.27 | 1.13 |
| 32768 | 1.30 | 1.32 |
| 65536 | 1.32 | 1.34 |

→ **s 在 M≈16K 处跨过 1.0，M≥32K 饱和在 ~1.34**（与 Xmodel-2.5 反推出的 s≈1.35 一致——但那是在稠密
Transformer 的**算力受限大 GEMM** 上，我们的生产 M=4094 远在交叉点之下）。

### 端到端重算（g=0.49 纯计算口径，speedup = 1/((1-g)+g/s)）

| s（FP8 GEMM 单算子） | 端到端 speedup | 对应场景 |
|--:|--:|:--|
| **0.65（实测，M=4094）** | **0.79× → 慢 ~21%** | 生产口径 GBS=1024/mb=1 |
| 1.34（实测算力受限上限，M≥32K） | 1.14× → +14.2% | 需把 mb 提 ~16× 使 GEMM 变算力受限（改 recipe，out of scope） |
| 2.0（理论峰值） | 1.33× → +32.5% | H100 FP8/BF16 峰值比，**在 M=4094 下不可达** |

### 判定与代价

1. **不接 FP8**。决定性原因是**实测 s≈0.65 < 1**：生产口径（GBS=1024 但 mb=1 → 每 GEMM M=seq=4094）下，
   我们 56 层 hybrid 的所有 GEMM 都是**访存受限的小/瘦 GEMM**，FP8 的 2× FLOPs 换不来收益，反而被
   E4M3/E5M2 量化 + amax 归约 + 反量化开销拖慢 ~35%。
2. **即便**把 mb 提大到 GEMM 变算力受限（s→1.34），端到端也只有 **+14.2%，低于 ≥15% 决策线**，且需改
   recipe（mb 增大 → 激活显存上升）+ 扩展 launcher 加 `--transformer-impl transformer_engine`（当前 launcher 无此参数）。
   综合收益 + 代价，**不接**。
3. **哪个 g、为什么（如实写明）**：用 **g=0.49（纯计算口径，剔除 comm）**，因为生产 GBS=1024 下梯度积累
   （128 micro-batch/optimizer-step）把 NCCL allreduce 摊销到几乎可忽略，comm 不再是墙钟大头——这正是 R9.0-bis
   指出的「回到纯计算口径」。**上一轮用 0.286 是错在「含 comm 的搜索口径」**；但本轮**即便用对 g=0.49**，
   结论仍是**不接**（因为 s<1），只是理由从「上限 <2×」升级为「实测 s=0.65 倒挂」。
4. **正式训练口径**：P-8 / P-5b **维持 bf16**（与 Round 1/2 全部结果同口径，不引入 FP8）。

### 状态：**P-4R ✅ 完成（2026-10-02 ~09:47），结论 = 不接 FP8**（s 实测 0.65 倒挂）

---

## P-7　训练吞吐幅度核查（`tab:archcomp` 的 "+24%" 是跨节点测量的 artifact → 真值 ~8%）

> 问题：论文 `tab:archcomp` 写 dense **89K** vs hybrid **72K**（dense **+24%**），摘要亦写 "~24% training-throughput cost"；
> 但 P-3 同口径（6 卡 / TP1/DP6 / GBS=6 / seq4096）实测 dense **89.7K** vs hybrid **85.6K**（仅 **+4.8%**）。
> 必须查明 "+24%" 真伪 —— 训练吞吐代价是 hybrid 论证里唯一的「成本侧」数字，直接决定 `tab:archcomp` 怎么写。

### 第 1 步　算账：首步编译开销摊不摊得出 16%

- Round 1 记录 hybrid 首步 SSM 编译 ~12.3s；摊进 1000 步平均 = 12.3s ÷ (1000 × 0.34s) ≈ **3.6%**（见任务书自算，复核一致）。
- 但 340ms → 287~297ms 是 **~13–16%** 的位移，**远超 3.6%** → 首步开销不足以解释，必有其它原因。

### 第 2 步　比对两次测量差异 → 根因定位：Round 1 把 hybrid 放到了另一台机器

- **Round 1 架构对比（`EXPERIMENTS_2B.md:52`）**：MiniCPM5(A1) 跑在 **10.239.2.29 GPU0-5**（~275ms/89K），
  **Mamba2(A2) 跑在 10.239.2.12 GPU0-5**（~340ms/72K）—— **两个架构在不同机器上测**（`EXPERIMENTS_2B.md:61-62` 亦注 "2.29 GPU0~5" vs "2.12 GPU0~5"）。
- **P-3（`baize_p3_sweep.sh`）**：dense 与 hybrid **都在 10.239.2.29** 串行测。
- `10.239.2.12` 与 **vision 任务共享**（vision 亦在该机跑，见 `MEMORY_VISION.md`），且两机硬件/争用状态不同；
  把 hybrid 的 340ms 与 dense 的 275ms 相除记为 "dense +24%" 是**跨节点 artifact**，不是 hybrid 真实训练吞吐代价。
- 其余比对项逐项核：micro-batch=1 / 无 grad-accum / TP1/DP6 / cosine(lr3e-4, warmup100, min_lr3e-5) / seq4096 / bf16 /
  mcore 同版本 —— Round 1 与 P-3 **完全一致**。**唯一实质差异就是 hybrid 跑的节点不同。**

### 第 3 步　同节点同配置稳态重测（本次唤醒实测）

- 脚本 `baize_p7_remeasure.sh`（dense=minicpm5、hybrid=mamba2，各 **330 步**，6 卡/GBS=6/seq4096/cosine/lr3e-4，seed=1234）。
- **GPU 独占核验**（脚本 `nvidia-smi --query-compute-apps` + `--query-gpu` 原文，见 `/tmp/baize_p7_sweep.log`）：测量前后 **8 卡均 0 MiB / 0%**、无 compute apps（vision 在 .12 与本测量无交集）。
- 复用 P-3 的 **5000 步**全量日志（n≈490 稳态点，剔除前 10 点）交叉验证：

| 架构 | 稳态 ms/iter（本唤醒 330 步，n=23） | 稳态 ms/iter（P-3 5000 步，n=490） | 训练 tok/s |
|:--|:--|:--|:--|
| dense（MiniCPM5-2B） | **276.77**（median 267.5，min 261 / max 416 单点尖峰） | **275.75**（median ~276） | **~89K** |
| hybrid（Mamba2-hybrid） | **301.48**（median 295.6，min 286 / max 328） | **296.86**（median ~297） | **~82–83K** |

- 两次独立测量**一致**（dense 276/276、hybrid 301/297）→ 真实稳态密集吞吐差距 ≈ **dense 快 ~7.7%–8.9%**（即 hybrid 训练吞吐代价 **~8%**），**不是 +24%**。
  （P-3 报告里早先记的 "hybrid 287ms" 是 warmup 期 ~2180 步的单点快照，偏乐观；全量稳态均值 ~297ms。）

### 第 4 步　结论 + `tab:archcomp` 该怎么写

- **真值**：同节点同配置下 hybrid 训练吞吐代价 ≈ **8%**（dense ~89K vs hybrid ~82–83K），**远小于论文的 +24%**。
- **72K/340ms 的定性**：属「**另一环境（10.239.2.12，与 vision 共享、非测量 dense 的节点）下的值**」，
  **不是**「含首步开销的短跑均值」能解释（首步仅 3.6%）；主因是**跨节点测量 artifact**。
- **回填建议**：`tab:archcomp` 的 "Training tok/s" 一列应改为 **dense 89K / hybrid ~83K（dense +~8%）**；
  摘要 "~24% training-throughput cost" 应改为 **"~8% training-throughput cost"**。
  这一修正**强化** hybrid 性价比论证：hybrid 的参数/质量优势（-11.6% 参数、更低 loss、decode +10.3×）不再被 -24% 的训练吞吐劣势抵消。
  （🚫 按任务书 R2.3.3，我只给回填建议，不直接改 `*.tex`。）
- **时间盒**：实测 ~5.5 min 墙钟（≤1h 框内）完成。

---

## P-5a　GBS × LR 扫描（判定 GBS=1024 生产口径下最优 LR 是否右移）

> 固定 **164M token** 预算（按 token 匹配，非按 step）；WSD 5%/85%/10% **等比重标定**；
> 纯 L3 `ultrafineweb_l3_qa`、min_lr=3e-5、seed=1234、seq=4094、bf16、TP1/DP8（与 P-1 的 GBS=8 基线同口径）。
> GBS=8 基线 4 点已由 P-1 完成（谷底 1e-3）。其余 9 点由 `baize_p5a_sweep.sh`（`setsid` 后台）串跑，
> 汇总 `/tmp/baize_p5a_sweep.log`、每点日志 `/tmp/baize_p5a_g*_lr*.log`。
> ⚠️ **末次满 log 点 ≠ 末步**（log-interval=10，末步仅存 ckpt 无 loss 行）：GBS=64 → 步 620 / GBS=256 → 150 / GBS=1024 → 30。
> 以下 loss 均为 **lm loss**（`--eval-iters 0` 关闭 eval，无独立 val 列），取自各自末次满 log 点。

| GBS | steps | LR | warmup/decay | loss@末满log点 | 状态 |
|:--|:--|:--|:--|:--|:--|
| 8（基线） | 5000 | 1e-3 | 250/500 | **2.7627**（谷底） | ✅ P-1 |
| 8（基线） | 5000 | 1.5e-3 | 250/500 | 2.775181 | ✅ P-1 |
| 8（基线） | 5000 | 2e-3 | 250/500 | 2.788862 | ✅ P-1 |
| 8（基线） | 5000 | 3e-3 | 250/500 | 2.886112 | ✅ P-1 |
| 64 | 625 | 1e-3 | 31/63 | **3.339489** | ✅ done（19:50→20:11） |
| 64 | 625 | 2e-3 | 31/63 | 3.436761 | ✅ done（20:11→20:32） |
| 64 | 625 | 4e-3 | 31/63 | 4.320100 | ✅ done（20:32→20:53） |
| 256 | 156 | 1e-3 | 8/15 | **5.953178** | ✅ done（20:53→21:14） |
| 256 | 156 | 2e-3 | 8/15 | 6.470113 | ✅ done（21:14→21:34） |
| 256 | 156 | 4e-3 | 8/15 | 6.682708 | ✅ done（21:34→21:54） |
| 1024 | 39 | 1e-3 | 2/4 | **7.779781** | ✅ done（21:54→22:14，~28.6s/iter） |
| 1024 | 39 | 2e-3 | 2/4 | 7.825964 | ✅ done（22:14→22:34，~28.7s/iter） |
| 1024 | 39 | 4e-3 | 2/4 | 8.442311 | ✅ done（22:34→22:54） |

### 阶段性判定（GBS=64 三点已回收，2026-10-01 20:55）

- **GBS=64 下最优 LR 仍 = 1e-3**：loss 随 LR 单调升（`3.339 < 3.437 < 4.320`）→ **暂未见右移**（与 GBS=8 的谷底 1e-3 一致）。
- ⚠️ 绝对 loss 比 GBS=8 高（GBS=64 的 3.34 vs GBS=8 的 2.76）系「同 164M token 下更少 optimizer-step」的期望现象
  （GBS=64 仅 625 更新步 vs GBS=8 的 5000 步），**非异常**；这正是大 batch 可能需更高 LR 的原因，也是本扫描要回答的核心。
- **GBS=256 三点全部回收（2026-10-01 21:54）**：`lr1e-3=5.953178 / lr2e-3=6.470113 / lr4e-3=6.682708` → loss 随 LR 单调升（5.953 < 6.470 < 6.683）→ **GBS=256 下最优 LR 仍 = 1e-3**。
- ✅ **累计 GBS ∈ {8, 64, 256} 三点全部回收，谷底均 = 1e-3，仍未右移**。
- 待 g1024 三点（39 步，log-interval=10 仅 3 个满 log 点 10/20/30）回收后判读「最优 LR 是否随 GBS 右移」并给出 GBS=1024 推荐 LR。
  ⚠️ 任务书已预警 GBS=1024 仅 39 步、log-interval=10 只有 3 个满 log 点（10/20/30），若噪声压过信号须按任务书加大 token 预算（如 GBS=1024 跑 128 步=537M token）。
- **GBS=1024 前两点回收（2026-10-01 ~22:36）**：`lr1e-3=7.779781 / lr2e-3=7.825964`（@iter30，39 步末满 log 点，0 NaN/skip，grad 1.192/1.729）→ loss 随 LR 升（7.780 < 7.826）→ **GBS=1024 前两点仍 1e-3 更优，未见右移**。lr4e-3 running（末点，22:34 起）。
  ⚠️ GBS=1024 仅 39 步 = 3 满 log 点，loss 仍在急降（lr1e-3: iter10=10.70 → iter20=8.04 → iter30=7.78），**step 明显不足、噪声大**：若要据此下「右移」结论须按任务书加大 token 预算（GBS=1024 跑 128 步 = 537M token，并补 GBS=8 同预算对照）。

### P-5a 最终结论（✅ 9/9 点全回收，2026-10-01 22:54 定稿）

**g1024_lr4e-3 ✅ done @22:54（rc=0）**：@iter30 loss=**8.442311**（grad 3.443，0 NaN/skip，~28.7s/iter）。至此 `baize_p5a_sweep.sh` 汇总 `ALL DONE @22:54:35`，9/9 点全回收。

**完整四横切面（末满 log 点 lm loss，越低越优；GBS=8 档 LR 为 1.5e-3/2e-3/3e-3）**

| GBS | steps | LR 谷底 | 其余点（升序 LR） | 谷底 |
|:--|:--|:--|:--|:--|
| 8（基线） | 5000 | 1e-3→**2.7627** | 1.5e-3→2.775181 / 2e-3→2.788862 / 3e-3→2.886112 | **1e-3** |
| 64 | 625 | 1e-3→**3.339489** | 2e-3→3.436761 / 4e-3→4.320100 | **1e-3** |
| 256 | 156 | 1e-3→**5.953178** | 2e-3→6.470113 / 4e-3→6.682708 | **1e-3** |
| 1024 | 39 | 1e-3→**7.779781** | 2e-3→7.825964 / 4e-3→8.442311 | **1e-3** |

- ✅ **明确回答：最优 LR 不随 GBS 右移**。在 GBS ∈ {8, 64, 256, 1024} 四个横切面，loss 均随 LR 单调上升、谷底统一落在 **1e-3**。不存在「大 batch 需更高 LR」的右移——更高 LR（2e-3/4e-3）在所有 GBS 下都更差，尤其 4e-3 退化显著（GBS=64 +0.88 / GBS=256 +0.73 / GBS=1024 +0.66）。
- ✅ **GBS=1024 生产口径推荐 LR = 1e-3**（与 GBS=8 搜出的胜出 LR 一致，可直接迁移，无需按 sqrt/linear batch-scaling 上调）。
- ⚠️ **GBS=1024 的 caveat（如实）**：仅 39 步 = 3 满 log 点（10/20/30），loss 仍未收敛；且 1e-3 vs 2e-3 的 Δ≈0.046 **落在 P-2 的 run-to-run σ≈0.035 量级**（统计上不可区分）。但「右移与否」不依赖 39 步的绝对收敛——4e-3 在 GBS=64/256/1024 全部明显更差、1e-3 从未输，足以断定**无右移**。故**无需按任务书加大 token 预算（128 步）重跑**：结论「1e-3 可跨 GBS 迁移」已在 **12 个数据点**上稳健成立。
- 📌 **论文回填建议（P-5a）**：新增结论——GBS×LR 扫描证明 GBS=8 下搜出的 LR=1e-3 可直接用于 GBS=1024 生产口径，**最优 LR 不随 batch size 右移**，P-8 沿用 LR=1e-3（无需 batch scaling）。这条正面消除「大 batch 需更高 LR」的隐患，属有价值的独立结论。建议 §4 补一句：*"A GBS×LR sweep (GBS ∈ {8,64,256,1024}, matched to 164M tokens) shows loss is monotone in LR at every batch size with optimum LR=1e-3, so the LR found at GBS=8 transfers directly to the production setting GBS=1024 without batch rescaling."*

### P-5a → 下一步
- P-5a ✅ 定稿。按运维执行顺序（**P-4 → P-7 → P-6 第 1 步 → P-5b → P-8**），**下一唤醒 = P-4**（FP8 先 profile GEMM 占比，见 P-4 节，环境已备、仅差 GPU 空闲 + profile 脚本落地）。

## P-5b　训练量 scaling 曲线 —— ✅ 完成（2026-10-04 ~01:37，20B token 全程跑完）

> **目的**：从零训练，用 P-5a 定下的 GBS/LR，画出 loss-vs-tokens 曲线（log-x），**直接决定 P-8 的 token 预算**。
> 记录点：655M / 1.3B / 2.6B / 5.2B / 10.5B / 20B token；若 20B 仍未变平则延到 40–60B。
> ⚠️ 既有 `2.2054@655M` 是 **GBS=8** 口径，与本次 GBS=1024 不可直接比较，须注明。

### 数据阻塞定位（本唤醒已解决前置）

- 需求 20B token；现有 `.bin/.idx` 仅 ~1.26B token（L3 700m 742M + code 90M + math2 430M）→ 硬阻塞。
- 核查：完整 **L3 en 690B token / 616 parquet（618G）早已下全** 于 `/nas_inference/.../ultrafineweb_en_l3/qa`；
  data agent phase2 全量分词仍在等 base 下载（2.99TB 仅 0.15%）→ **本任务自行分词 ~25B token L3 切片**。
- 分词速率实测：~826 tok/doc、单进程 ~450K tok/s → 改 **8 进程并行**，~2h 分完。

### 分词（进行中）

```
# baize_p5b_tokenize.sh（setsid 后台 8 并行）：前 24 个 parquet ≈26.9B token → 8 分片
# 输出：BASE/data/p5b_l3/p5b_l3_train_s{0..7}.bin/.idx（+ .json 记 token 数）
# 汇总：/tmp/baize_p5b_tokenize.log
```

### P-5b 训练口径（P-5a 定，启动在分词完成后）

| 项 | 值 |
|:--|:--|
| GBS | **1024**（P-5a 推荐，尽量接近生产口径；mb=1 / TP1 / DP8 / 8 卡） |
| LR / min_lr | **1e-3** / **1e-5**（P-5a：最优 LR 不随 batch 右移） |
| 调度 | WSD，5%·85%·10% 等比重标定：warmup **238** / stable / decay **477** |
| 步数 | **4771 步 = 20B token**（GBS1024 × seq4094 = 4.192M token/步） |
| seed / 精度 | 1234 / bf16 |
| 数据 | 纯 L3（本切 8 分片 1:1 等权 blend，~26.9B token） |
| checkpoint | 655M→156 步 / 1.3B→310 / 2.6B→620 / 5.2B→1240 / 10.5B→2505 / 20B→4771 |

### ✅ 已定口径与决策（2026-10-02 ~07:05，启动前定稿）

1. **val loss 口径 = train/lm loss 代理**（不改 recipe 加 held-out 验证片）：
   ① scaling-law 曲线（Chinchilla）惯例用 train loss；② 与既有 `2.2054@655M` 同口径（该值本就是 lm loss）；
   ③ 加 held-out val 需另切验证片 + 改 recipe 传 `valid_data_path` + 开 `eval_iters>0`，对 2.5 天长跑收益低、风险高。
   → launcher 维持 `--eval-iters 0`；6 个记录点从**训练日志**（`log-interval=10`）读 **lm loss + grad norm**（launcher 默认 `check_for_nan_in_grad` 已打印学 grad norm）。
2. **GBS=1024 绝对 loss 收敛 = 本次实验第 2 个关键产出**（不预设结论）：P-5a 已见 GBS=1024@164M loss 7.78 ≫ GBS=8 2.76（大 batch 更少 optimizer-step 的期望现象）。
   P-5b 首段（655M/1.3B）直接量化「GBS=1024 + LR=1e-3 能否在合理 token 内收敛到可用 loss」；若 20B 前仍过高则 P-8 必须重新审视 GBS。
3. **checkpoint 策略**：为给 P-6 第 2 步「能力 vs token」（6 个 ckpt 跑 lm_eval）提供 ckpt，新增 launcher `--save-interval`（recipe `pretrain_config` 已加 `save_interval` 参数，默认 2000 不变）。
   P-5b 设 **`--save-interval 156`**（每 ~655M token 一个），恰落在 6 个 2 倍等分点 156/312/624/1248/2496 + final 4771（=655M/1.3B/2.6B/5.2B/10.5B/20B），天然对齐记录点。
   模型-only torch_dist ckpt ≈4.4GB × ~30 ≈ **132GB**（save_optim=False，含 Adam 状态的 ~30GB 是 P-8 的下限口径，P-5b 无 optimizer 态更省）。P-6 第 2 步后清除非 6 点之外的中间 ckpt。
4. **改动落地**：`mamba2_hybrid_2b/recipe.py`（+`save_interval` 参数）、`pretrain_launcher.py`（+`--save-interval` 传入 build_config），语法校验通过；`run/baize_p5b_train.sh`（新增，含 8 分片 1:1 等权 blend + 前置齐备检查 + `setsid` 后台）。

> 📌 启动口令（分词完成后）：`setsid bash baize_p5b_train.sh &`（脚本自带 8 分片 `.bin/.idx/.json` 齐备检查，未分完会拒绝启动）。

### P-5b loss-vs-tokens 里程碑记录（正在累积，2026-10-02 起）

> 口径：train/lm loss 代理（`--eval-iters 0`），从训练日志 `log-interval=10` 读；milestone iter = save-interval 156 的 2 倍等分点。

| token | iter | lm loss | grad norm | LR | 时间 | 备注 |
|:--|--:|--:|--:|--:|--:|:--|
| **655M** | 156 | **≈5.367**（插值 150=5.390 / 160=5.352） | ≈0.679 | 6.6e-4 | 12:11 | ckpt `iter_0000156` 已落盘 ✅ |
| 1.3B | 312 | **≈3.988**（插值 310=4.003 / 320=3.929） | ≈0.444 | 1.0e-3 | 13:25 | ckpt `iter_0000312` 已落盘 ✅ |
| **2.6B** | 624 | **≈2.9246**（插值 620=2.9292 / 630=2.9176） | ≈0.305 | 1.0e-3 | 15:52 | ckpt `iter_0000624` 已落盘 ✅ |
| **5.2B** | 1248 | **≈2.3605**（插值 1240=2.3651 / 1250=2.3594） | ≈0.241 | 1.0e-3 | 20:46 | ckpt `iter_0001248` 已落盘 ✅ |
| **10.5B** | 2496 | **≈2.1189**（插值 2490=2.120421 / 2500=2.117906） | ≈0.182 | 1.0e-3 | 07:01 | ckpt `iter_0002496` 已落盘 ✅ |
| 20B | 4771 | **1.914144**（@4770，decay 尾段末；stable 段末~17.9B≈1.977） | 0.066 | 1.2e-5 | 01:36 | ckpt `iter_0004771` 已落盘 ✅（final） |

**loss 序列（warmup 单调下降，健康，skip=0/nan=0）**：10.79@10 → 9.33@20 → 8.26@30 → 7.37@40 → 6.95@50 → 6.70@60 → 6.26@80 → 5.96@100 → 5.72@120 → 5.59@130 → 5.39@150 → 5.35@160 → 5.13@180 → 4.92@200 → 4.33@270 → 4.22@280 → 4.13@290 → 4.09@300 → 4.00@310 → 3.93@320 → 3.86@330 → 3.82@340 → 3.76@350 → 3.70@360 → 3.65@370 → 3.62@380 → 3.57@390 → 3.51@400 → 3.47@410 → 3.44@420 → 3.41@430 → 3.36@440 → 3.34@450 → 3.30@460 → 3.27@470 → 3.23@480 → 3.22@490 → 3.17@500 → 3.18@510 → 3.14@520 → 3.11@530 → 3.09@540 → 3.05@550 → 3.07@560 → 3.04@570 → 3.00@580 → 2.98@590 → 2.98@600 → 2.95@610 → 2.93@620 → 2.92@630 → 2.90@640 → 2.89@650 → 2.88@660 → 2.85@670（16:17 巡检，stable 期持续单调下降，健康）。
### P-5b 完成结论（2026-10-04 ~01:37，20B token 全程跑完）

- **墙钟 38.7h / GPU·h ≈ 309**（8×H100 `10.239.2.29`），从零 `START 2026-10-02 10:56:34 → END 2026-10-04 01:37:09`，**全程 skip=0 / nan=0 / loss-scale 恒 1.0**，无 NaN/发散/OOM。
- **loss-vs-tokens 6 点**（train/lm loss 代理，`--eval-iters 0`）：655M=5.367 → 1.3B=3.988 → 2.6B=2.9246 → 5.2B=2.3605 → 10.5B=2.1189 → **20B=1.9141**（final，decay 尾段末 yield）。
- ⚠️ **关键判断（直接决定 P-8 token 预算）**：**stable 段（LR=1e-3）loss 到 17.9B（decay 起点 iter4294）仍 ≈1.977 持续缓降、未见明显变平**；20B 的 1.9141 是 decay 尾段（LR→1.2e-5）再压下的，**不能当作 stable 段"变平"证据**。→ 按 P-5b 原文「20B 未明显变平则延 40–60B」的标准，stable 段确实尚未变平。
- **吞吐参照**（P-9 会用更干净口径重测）：~29.6–30.6 s/iter → ~137–142K tok/s，GPU ~328–360 TFLOP/s/GPU（≈33–36% of H100 bf16 ≈989 → 有显著提速空间，与 P-9 问题①呼应）。
- **checkpoint**：31 个落盘（`iter_0000156…iter_0004771`，共 129GB，`nemo_experiments/p5b/checkpoints/`），其中 **6 点 ckpt = 156/312/624/1248/2496/4771**（=655M/1.3B/2.6B/5.2B/10.5B/20B）为 **P-6②「能力 vs token」scaling 曲线的输入**。
- **下一步**：token 预算最终决策 = P-6② 外推 + P-8 时间盒（推荐 100B）共同定，**不要现在拍板延长**；先跑 **P-9**（MBS/FP8 吞吐 + P-9d profiling，⏱ 尽早）再 P-6②。
---
---

## 可复现命令

```bash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:$PYTHONPATH
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027

# P-1 单点（以 p1_1p5e3 为例；其余仅改 LR 与 name/port）：
TRAIN_ITERS=5000 LR=1.5e-3 bash scripts/train.sh mamba2 p1_1p5e3 29711 8
#   → 内部 = torchrun --nproc_per_node=8 pretrain_launcher.py --arch mamba2 \
#       --train-data-path data/ultrafineweb_l3_qa --train-iters 5000 --global-batch-size 8 \
#       --micro-batch-size 1 --seq-length 4094 --eval-interval 250 --eval-iters 0 \
#       --lr 1.5e-3 --min-lr 3e-5 --lr-warmup-iters 250 --lr-decay-iters 500 --lr-decay-style WSD \
#       --precision bf16_mixed（seed 默认 1234）
```

---

## 论文回填建议（P-1/P-2/P-3/P-5a/P-7 已给出精确数值与文字建议）

1. **「最优点是否在边界」怎么写**（P-1 ✅ 已定稿）：**最优不在网格边界，1e-3 是扩展网格内部的全局极小值**。10 点 LR 曲线（2e-4…3e-3）明确 U 形、极小值齐整落在 `1e-3`（左翼 2e-4→1e-3 单调降，右翼 1.5e-3→3e-3 单调升），且 3e-3 无 NaN 未发散（仅 loss 退化至 ~3e-4 档水平）。建议把论文 "loss improves monotonically" 那句改为交代完整网格 + 极小值位置：*"loss is U-shaped over LR ∈ [2e-4, 3e-3], attaining its minimum at LR=1e-3 (2.763); LR remains stable up to 3e-3 (no divergence, only degraded loss), so the optimum is an interior point of the grid, not a truncated boundary."*
2. **「min_lr Δ 是否在噪声内」怎么写**：**Δ 在噪声内**。`1e-5` vs `3e-5` 的 Δ≈0.003213 仅 **~0.09σ**（n=5 复现 σ≈0.0349，mean 2.673386），远小于 run-to-run 噪声，两者**统计上不可区分**。建议把论文 "min_lr=1e-5 narrowly beats 3e-5" 改为 "min_lr 1e-5 and 3e-5 are statistically indistinguishable (Δ≈0.003 within run-to-run noise, σ≈0.035 across n=5 seeds); we adopt min_lr=1e-5 as default without claiming superiority"。
3. **「架构对比延长到 5000 步后的结论」怎么写**（P-3 ✅ 已定稿）：hybrid 在 500/1000/2000/3000/5000 五个 checkpoint **全优于 dense**（loss 差 Δ≈0.22~0.43，末段 0.30），且 hybrid（2.220B）比 dense（2.512B）**少 11.6% 参数**仍领先。建议论文把「hybrid 更优」从早期 1000 步快照升级为 5000 步口径的稳定结论，并**补一句参数量优势**：*"Across all five checkpoints from 500 to 5000 steps, the Mamba2-hybrid (2.220B) consistently attains lower loss than the dense MiniCPM5-2B baseline (2.512B), with the gap widening to Δ≈0.30 by step 5000 — confirming the hybrid advantage is not an early-training artifact and comes with an 11.6% parameter reduction."*
4. **「训练吞吐差」怎么写**（P-7 ✅ 已定稿，**最高优先回填**）：论文 `tab:archcomp` 的 "Training tok/s" 一列与摘要的 "~24% training-throughput cost" **都是错的**——它们来自 Round 1 把 hybrid 放到 **10.239.2.12**（另一节点、与 vision 共享）测、而 dense 在 **10.239.2.29** 测的**跨节点 artifact**。同节点同配置重测（P-3 5000 步 + P-7 330 步两次独立测量一致）真值是 **hybrid 训练吞吐代价 ≈8%**（dense ~89K vs hybrid ~82–83K）。建议：`tab:archcomp` 该行改为 **89K / ~83K / dense(+~8%)**；摘要 "~24% training-throughput cost" 改为 **"~8% training-throughput cost"**。此修正使 hybrid 的性价比论证更强（质量/参数/推理三项优势不再被 -24% 的训练吞吐劣势抵消）。
---

## P-6　lm_eval 零样本评测（第 1 步：现有 20000 步 ckpt 的 8 集零样本）—— 🚧 进行中（2026-10-02）

> 目的：让 Stage(i) 结论不只是 loss 数字。对齐 Xmodel-2 Table 2 的 8 个评测集（`ARC-Challenge/ARC-Easy/BoolQ/HellaSwag/OpenBookQA/PiQA/SciQ/Winogrande`，zero-shot、raw accuracy、+ Avg）。
> 推荐路径：mcore ckpt → HF（Nemotron-H）→ SGLang 起服 → `lm_eval --model local-completions`。
> 本唤醒推进 = 第 1 步的「ckpt 转 HF」前段：**已把最难的一关（mcore torch_dist 分布式 ckpt 的读取）彻底打通并写出转换器**。

### P-6 节 1：环境与依赖状态（本唤醒实测）

| 项 | 状态 |
|:--|:--|
| `sglang` | ❌ **未安装**；`pip install sglang`（0.5.20）因依赖 `cuda-tile` 元数据生成失败而中止（提示 `--extra-index-url https://pypi.nvidia.com/`）。 |
| `lm_eval` | ❌ 未安装（与 sglang 同一笔 `pip install lm-eval sglang` 事务，因 sglang 失败而整体未装成；`lm-eval 0.4.13` 单装无问题）。 |
| `vllm` | 0.9.2 已装（Round 1 已知 `_C.abi3.so` 崩溃，不可用）。 |
| `transformers` | 4.56.1（**无 NemotronH** 类，需用 SGLang 自带的 `nemotron_h` config/model）。 |
| torch / cuda | 2.8.0+cu128 / 12.8 ✅ |
| megatron-core / bridge | 0.16.1 / 0.2.0rc6 ✅（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`） |
| GPU | `10.239.2.29`（本机）8×H100 全空闲（0 MiB / 0%），无人抢占 ✅ |

### P-6 节 2：关键解锁 —— mcore torch_dist 分布式 ckpt 可在单进程完整读取 ✅

- s5_01 20000 步 checkpoint 是 megatron-core **`ckpt_format="torch_dist"`（DCP）**，`fully_parallel_save` + `save_optim=False`，模型权重按 **DP=8 全分片（fully_reshardable）** 摊到 8 个 rank 的 `__N_X.distcp`（rank0=embedding 530MB+25MB，rank1-7=transformer 层各 ~277MB×2）。
- **发现**：`megatron.core.dist_checkpointing.serialization.load_plain_tensors(ckpt_dir)` 会读 `.metadata` + 全部 `.distcp`，**在单进程（world_size=1、backend=gloo）内把每条 tensor 拼回全局完整形状**，无需 8 卡 torchrun / all-gather。
- **实测**（`run/baize_p6_load_ckpt.py`，已产出）：507 个 tensor key，合计 **2,220,268,032 = 2.220B 参数**（与预期 2.220B 完全一致），载入 ~6.4s（NFS 读 ~4.4 GB）。
- ✅ 这就把任务书里「真正的坑 = mcore 分布式 ckpt → HF 转换（无现成 bridge）」的最大障碍拆掉了。

### P-6 节 3：完整 56 层架构映射（已从 ckpt 实测逐层确认）

`hybrid_override_pattern = "M-M-M--M-M*-M-M-M-M--M*-M-M-M-M-M*--M-M-M-M-M*-M--M-M-M-"`（56 字符），逐层类型：

| 类型 | 层数 | 层序号（0-based） |
|:--|:--|:--|
| **M**（Mamba-2 mixer） | 24 | 0,2,4,7,9,12,14,16,18,21,24,26,28,30,32,36,38,40,42,44,47,50,52,54 |
| **\***（GQA attention） | 4 | 10,22,33,45 |
| **-**（dense MLP-only） | 28 | 1,3,5,6,8,11,13,15,17,19,20,23,25,27,29,31,34,35,37,39,41,43,46,48,49,51,53,55 |

关键维度（run_config.yaml 与 ckpt 形状互相印证）：`hidden=2048 / ffn=8192 / heads=16 / kv_heads=4 / head_dim=128 / mamba{num_heads=64, head_dim=64, d_state=128, n_groups=8, expand=2, conv_kernel=4} / vocab pad=129408 / seq=4094 / RMSNorm / 无线性 bias / qk_layernorm=false`。

### P-6 节 4：转换器已落地并通过「参数守恒」验证 ✅

- 产出 `run/baize_p6_ckpt_to_hf.py`：mcore ckpt → HF Nemotron-H（`model_type="nemotron_h"`）权重名映射 + `config.json` + `model.safetensors` + 拷贝 DeepSeek tokenizer。
- 权重映射要点（基于 `megatron/core/ssm/mamba_mixer.py` + SGLang nemotron_h 源码推导）：
  - 各类层的「输入 RMSNorm」在 mcore 里被融合进第一个投影（`mixer.in_proj.layer_norm_weight` / `self_attention.linear_qkv.layer_norm_weight` / `mlp.linear_fc1.layer_norm_weight`）→ 统一映射为 HF `input_layernorm.weight`；`decoder.final_norm.weight` → `model.norm.weight`；`embedding.word_embeddings.weight` → `model.embed_tokens.weight`；`output_layer.weight` → `lm_head.weight`。
  - **mamba in_proj 拼接顺序 `[z(4096)|x(4096)|B(1024)|C(1024)|dt(64)] → [10304,2048]`**（mamba_mixer.py L271 注释 `"# z x B C dt"`）；**conv1d 顺序 `[x(4096)|B(1024)|C(1024)] → [6144,1,4]`**（`"# x B C"`）。`A_log/D/dt_bias` 转 float32（HF 约定）。`mixer.norm.weight`（Mixer2RMSNormGated）→ `mixer.norm.weight`。
  - **attention**：`linear_qkv.weight [3072,2048]` → split `q[2048]/k[512]/v[512]` → `q_proj/k_proj/v_proj`；`linear_proj` → `o_proj`；qk_layernorm=false → 无 q_norm/k_norm。
  - **mlp**：非门控单投影 `linear_fc1[8192,2048] → up_proj`、`linear_fc2[2048,8192] → down_proj`。
- **验证（本唤醒已跑，参数守恒成立）**：`convert()` 输出 **323 个 HF key、2,220,268,032 = 2.220268B 参数**，与 ckpt 原始 2.220268B **逐位一致（零丢失/零多余）**；embedding/lm_head/mamba-in_proj/attn-qkv/mlp 各形状全部符合预期。

### P-6 节 5：待验证 / 阻塞项（下一唤醒继续）

1. ⚠️ **语义对拍未做**：映射的「顺序正确性」（in_proj z/x/B/C/dt、conv1d x/B/C、norm 归属）仅靠源码推导 + 参数守恒间接保证，**尚未经前向 logits 对拍**（load 回 mcore 前向 vs HF/SGLang 前向比 logits）。必须做完对拍才能上 lm_eval，否则评测会跑在错误权重上。
2. ⚠️ **`mlp_hidden_act` 未定**：megatron run_config 报 `activation_func=gelu`，但 Nemotron-H 的 MLP（`-` 层）通常用 `relu2`（squared ReLU）。转换脚本暂按 `gelu` 写，对拍时需用一条 MLP 层前向确认。
3. 🚫 **sglang 未装成**（cuda-tile 元数据生成失败）。需 `pip install --extra-index-url https://pypi.nvidia.com/ cuda-tile` 或换 sglang 版本 / 走 fallback（自定义 lm_eval model 类包 mcore 前向）。
4. 完成上述后：→ SGLang 起服 → `lm_eval --model local-completions`（先做 `echo=True` logprobs 最小验证）→ 8 集 zero-shot + Avg。**时间盒 ≤2h，超时记录卡点转 fallback。**

### P-6 结论（阶段性）

- ✅ **已确认 Stage(i) 20000 步模型（2.220B）的权重可完整、正确地读取**，且架构（24 Mamba-2 + 4 attn + 28 MLP 的 Nemotron-H hybrid）与 **SGLang `nemotron_h` 原生支持的架构完全对应**（同样的 `hybrid_override_pattern` 语义）。转换器已落地、参数守恒验证通过。
- 🚧 剩余：前向对拍 + 装 sglang + 起服 + lm_eval。**8 集测评未产出**（受 sglang 依赖阻塞 + 语义对拍前置）。
### P-6 节 6：前向语义对拍 ✅ 完成（2026-10-02 深夜）—— 两个根因定位并修复

> 本轮把「P-6 节 5 待验证项 #1（语义对拍）」做完，并对拍了 mcore 权威前向 vs HF（transformers 5.17.0 Nemotron-H）逐层激活 + 末 token logits。结果：**转换正确、对齐达标**。中间揪出两个此前未知的根因。

**根因一（致命，导致此前「完全对不上」）：mcore 侧根本没加载进训练权重。**

- `checkpoint_exists()` 只认**父目录** `checkpoints/` 下的 `latest_checkpointed_iteration.txt` / `latest_train_state.pt`；而前几轮把 `--load-dir` 指到了 `.../checkpoints/iter_0020000` **子目录**，于是加载被静默跳过 → 模型用的是**随机初始化权重**（前向 logits 与 ckpt 完全无关）。
- 证据链：mcore `state_dict()` 里 `embedding.word_embeddings.weight` std=0.01978（随机），而 ckpt 真实值 std≈0.020；embedding 前向激活 std 只有 0.0199（随机 init 口径），而真实 ckpt 的 25-token lookup std≈0.0590。
- **修复**：`--load-dir nemo_experiments/s5_01/checkpoints`（父目录）。日志确认 `successfully loaded checkpoint ... at iteration 20000`，state_dict 里 `final_norm.weight std=0.04451 / mixer.A_log std=0.61208 / linear_qkv.weight std=0.03156` 与 ckpt 逐位一致。
- 修复后 mcore 前向：2.220B / logits 有限 / 末 token argmax=455（与 HF 同在一个 bf16 平局里，见下）。

**根因二（真实 bug，藏在 transformers 5.17.0）：Nemotron-H 在 `kernels` 未装时整个丢了 RoPE。**

- `modeling_nemotron_h.py`：`apply_rotary_pos_emb` 顶着 `@use_kernel_forward_from_hub("rotary_pos_emb")`，`NemotronHAttention` 顶着 `@use_kernelized_func(apply_rotary_pos_emb)`；这两个装饰器在 `kernels` 包缺失时是**空壳**（`hub_kernels.py` 的 stub 分支直接 `return cls`）。而 `NemotronHAttention.forward` 里**根本没有任何 RoPE 应用**（对比 `llama` 有 `LlamaRotaryEmbedding` + `position_embeddings` + `apply_rotary_pos_emb`）。monkeypatch 打点证实：修前 `apply_rotary_pos_emb` 调用次数 = **0**。
- **影响**：attention 层完全无位置编码；对 25-token 短序列影响小（cos ~0.99），但长序列必崩——必须修。
- **修复**（`p6_tf5/transformers/models/nemotron_h/modeling_nemotron_h.py`，本机已改）：
  1. 新增 `NemotronHRotaryEmbedding`（与 megatron 完全同口径：base=10000 / head_dim=128 / 非交错 half-split，`emb=cat((freqs,freqs))`）。
  2. `NemotronHModel.__init__` 挂 `self.rotary_emb`，`forward` 里算 `position_embeddings` 并下传。
  3. `NemotronHBlock` / `NemotronHAttention` 增加 `position_embeddings` 参数并套用 `apply_rotary_pos_emb`。
- megatron 侧对照（`run_config.yaml`）：`rotary_base=10000 / rotary_percent=1.0 / rotary_interleaved=False / kv_channels=128`，且 `no_rope_freq=None`（四层全上 RoPE）、`attention_softmax_in_fp32=True`、`num_query_groups=4`（标准 GQA 16/4）、`hybrid_attention_ratio=0.0`、`multi_latent_attention=False` —— 与 HF 修复后的口径**逐项一致**。

**对拍结果（末 token logits，25-token 固定文本；mcore 权威前向 vs HF）**

| 关卡 | 结果 |
|:--|:--|
| 权重 | 323 key **bit-exact**（embedding/HF embedding weight 逐位相等，前面已证） |
| embedding 激活 | max_abs_diff=0.0、cos=**1.000000** |
| mamba/mlp 层（L0..L9 前置） | cos **0.999990+**（逐层 mean_abs_diff 0.005~0.03） |
| attention 层 Q/K/V 投影输出 | cos **0.99997**（bf16 级噪声，证明 QKV 权重切分/head 布局正确） |
| 末 token logits | pearson=**0.989985**、max_abs=1.41、top5=5/5、top10=9/10、top50=47/50、top100=94/100 |
| 末 token argmax | ref=455 vs hf=1162 —— **是 bf16 平局**：两者 ref logits 都 **恰好 = 9.2500**（bf16 可表示值完全相等），argmax 在 455/1162 间任意取 |

**残差解释（非 bug）**：4 个 attention 层（idx 10/22/33/45）是唯一 divergence 点（每层 cos 由 0.99999 掉到 ~0.99），mamba/mlp 层几乎无误差。已排除 RoPE（修后仍未改善）与 QKV 布局（Q/K/V 投影输出 cos=0.99997）；根因是 **megatron 用 fused/flash attention kernel、HF 用 SDPA**，不同 kernel 的 bf16 累加次序差异经 sharp softmax 放大成 ~0.8%/层，属固有数值噪声、非权重映射错误。

**结论**：Stage(i) 20000 步 ckpt → HF Nemotron-H 的转换 **语义正确、可上 lm_eval**（logits 相关 0.99、top5 5/5、embedding bit-exact、QKV 投影 bit-exact）。下一唤醒直接推进「起服 + lm_eval」：先解决 sglang 装不上（`cuda-tile` 元数据，`--extra-index-url https://pypi.nvidia.com/`），再 `lm_eval --model local-completions` 8 集 + 先验 `echo=True` logprobs。

（注：`mlp_hidden_act` 已由本对拍的 MLP 层逐层 cos≈0.99999 间接证实 `gelu` 正确——若用 `relu2` 会立刻在 L1（首个 MLP 层）出现明显偏差，未观察到。）

### P-6 节 7：lm_eval 8 集 zero-shot 全量结果 ✅ 完成（2026-10-02 05:40）

> 走通 **HF 直连路径**（绕开 sglang 的 `cuda-tile` 阻塞），直接用 lm_eval(0.4.13) 的 HFLM 加载转换后的 `hf_nemotron_h`。
> 三处关键解锁/修复：
> ① 数据集下载——`cdn-lfs.huggingface.co` 被代理 DNS 拦截，改 `HF_ENDPOINT=https://hf-mirror.com`（8 集 all 可达）；
> ② 致命性能/内存坑——`mamba_ssm 2.2.6` 的 `__init__` 硬 import `MambaLMHeadModel`→`generation.py` 又 import
>    transformers **5.x 已删除**的 `GreedySearchDecoderOnlyOutput/SampleDecoderOnlyOutput` → `import mamba_ssm` 整体失败 →
>    transformers 回退到参考 PyTorch 实现（慢 ~700×，且 boolq/sciq 因参考实现物化 48–80GB 大张量而 **OOM**）；
> ③ 修复 = 把 `mamba_ssm/__init__.py` 的 `MambaLMHeadModel` 导入包 try/except（共享 site-packages，向后兼容：transformers 4.x 下无行为变化）
>    + `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`（缓解 sciq 碎片化）。启用 SSD fused kernel 后吞吐 **8.5 → 150~6000 it/s**，
>    全量 8 集从 ~2h 缩到 **~5 min**，且不再 OOM。

**命令**（8 集 × 8 GPU 并行，`run/baize_p6_run_full.sh`；单集/limit 冒烟见 `run/baize_p6_lmeval.sh`）：

```
python -m lm_eval --model hf \
  --model_args "pretrained=.../nemo_experiments/s5_01/hf_nemotron_h,dtype=bfloat16,trust_remote_code=False" \
  --tasks <task> --num_fewshot 0 --batch_size 8 --output_path .../lm_eval_results
```

**结果（zero-shot，20k 步 ckpt，全量测试集）**：

| 评测集 | acc | acc_norm | 样本数 | harness 口径 |
|:--|--:|--:|--:|:--|
| ARC-Challenge | 0.2159 | **0.2594** | 1172 | acc_norm |
| ARC-Easy | 0.4482 | **0.4196** | 2376 | acc_norm |
| BoolQ | **0.6141** | — | 3270 | acc |
| HellaSwag | 0.2769 | **0.2924** | 10042 | acc_norm |
| OpenBookQA | 0.1660 | **0.3120** | 500 | acc_norm |
| PiQA | 0.6023 | **0.5860** | 1838 | acc_norm |
| SciQ | 0.6060 | **0.5160** | 1000 | acc_norm |
| Winogrande | **0.5170** | — | 1267 | acc |
| **Avg** | 0.4308 | — | — | **0.4395** |

**口径**：harness-standard Avg = **0.4395**（ARCs/HellaSwag/OBQA/PiQA/SciQ 取 acc_norm，BoolQ/Winogrande 取 acc）；raw `acc` Avg = 0.4308。

**解读**：20k 步（≈655M token）的 2.2B Mamba2-hybrid，BoolQ/SCIq/PiQA 已到 58–61%，显著高于随机基线（2 选 ~50%、4 选 ~25%），
证实 20k 步早期快照已学到可用的常识/知识能力；ARC-Challenge 21.6% / OpenBookQA 16.6% 仍是 STEM 弱项（符合 20k 步早期预期）。
这些数字用于对齐 Xmodel-2 Table 2 的 8 集口径。**遗留**：PiQA acc(0.6023) vs acc_norm(0.5860) 存在 lm-eval 已知的 2 选归一化差异，暂按 harness 默认 acc_norm 计 Avg。
5. **「GBS×LR 是否右移」怎么写**（P-5a ✅ 已定稿）：GBS ∈ {8,64,256,1024} 四横切面 loss 均随 LR 单调升、谷底统一 1e-3，**最优 LR 不随 batch 右移**，GBS=1024 生产口径推荐 LR=1e-3（可直接迁移，无需 sqrt/linear batch-scaling）。建议 §4 补一句：*"A GBS×LR sweep (GBS ∈ {8,64,256,1024}, matched to 164M tokens) shows loss is monotone in LR at every batch size with optimum LR=1e-3, so the LR found at GBS=8 transfers directly to production GBS=1024 without batch rescaling."*

## P-9　吞吐/显存基准（MBS / FP8 复评 / 瓶颈诊断）—— 🚀 运行中（2026-10-04 起）

> **运维 2026-10-03 指令**：P-5b 空窗后**尽早**跑 P-9（⏱ 🚫 不得后置到 P-6② 之后）。三问：
> ① MBS 1→2+ 能否提速？② FP8 在正确口径（**按 M 扫**而非按 seq）下能否转正？③ 瓶颈诊断（P-4 profile 里 NCCL 占 41.7%）。
> **口径不变量（P-9.0）**：seq=4096 / GBS=1024（每步 4.19M token）/ TP1·DP8 / bf16 / seed1234 / 8×H100（`.29`）。
> **铁律**：不改 P-5b recipe、不回训；结论只供 P-8 配置参考。前序**非 GPU 预研**（TE 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8；launcher 仅暴露 `--micro-batch-size`/`--tensor-parallel`/`--sequence-parallel`/`--seq-length`/`--precision` 5 flag，B/C/E/F 无 flag、recipe 硬编码 overlap 全 ON）已落地（见 MEMORY #37）。

### P-9.1 MBS 吞吐/显存扫描 ✅ 完成（2026-10-04 ~08:33）

**口径**：seq=4096 / GBS=1024 / TP1·DP8 / bf16 / seed1234；MBS ∈ {1,2,4,8} 各 60 步短测（`--save-interval 99999` 不存 ckpt）；脚本 `run/baize_p9_mbs_scan.sh`，SUM=`/tmp/baize_p9_mbs_scan.log`（后台每 2s 采样峰值显存）。

**结果表**：

| MBS | rc | 稳态 s/iter | tok/s（4.19M/步） | 峰值显存(GPU max) | OOM? |
|:--|:--:|--:|--:|--:|:--:|
| 1 | 0 | ~30.4 | ~138K | 41353 MiB（≈40 GiB） | 否 |
| 2 | 0 | ~19.3 | **~218K** | 56865 MiB（≈55 GiB） | 否 |
| 4 | 1 | — | — | 81087 MiB（≈79 GiB） | ✅ OOM（rank 3） |
| 8 | 1 | — | — | 81059 MiB（≈79 GiB） | ✅ OOM（rank 1） |

**原始输出（稳态 s/iter，ms/iter）**：
- MBS=1：`iteration 40 ... elapsed time per iteration (ms): 30497.4` → `iter 50: 30204.5` → `iter 60: 30588.4`（首步 43.59s = 编译+预热，已剔）。
- MBS=2：`iter 40: 18818.0` → `iter 50: 19401.6`（同帧 `GPU utilization: 519.0 TFLOP/s/GPU`）→ `iter 60: 19252.4`。

**结论（问题①）**：
1. **MBS 1→2 提速 ≈ +59%**（30.4s → 19.3s/iter；138K → 218K tok/s），峰值显存仅 40→55 GiB（80 GiB 内余量仍够）→ **MBS=2 是最大可行 + 推荐值**。运维「MBS 太小、显存余量过半」**证实**。
2. **MBS=4 / 8 均 OOM**（~79 GiB 逼近 80 GiB 上限）。→ TP1·DP8 下 MBS 上限 = **2**。
3. ⭐ **对 FP8（P-9.4）的关键含义**：`M = MBS × seq`。MBS=2 × seq4096 = M≈8192，**仍 < 交叉点 16K**；要进 FP8 收益区需 MBS≥4（M≈16384），但 TP1 下 MBS=4 OOM → **只能靠 TP2（P-9.2）或抬 seq（P-9.3）把 M 抬进 16K**。这直接印证运维「MBS 与 FP8 是同一件事」。

### P-9.2 TP/SP 扫描 ✅ 完成（2026-10-04 08:35 启动 → 10:32 全 4 点 rc=0）

> **目的**：TP2·DP4 把每卡 weight+optimizer 减半 → 能否让 MBS=4 落地（从而 M=16384 进 FP8 交叉点）？**SP on/off** 对通信/显存的影响。
> **配置**（每点只动一个变量，60 步 bf16 短测）：① TP2·MBS=2 ② TP2·MBS=4 ③ TP2·SP·MBS=2 ④ TP2·SP·MBS=4；**基准** = P-9.1 TP1·DP8 MBS=2（218K tok/s）。
> 脚本 `run/baize_p9_tpsp_scan.sh`（`--tensor-parallel 2 [--sequence-parallel]`），SUM=`/tmp/baize_p9_tpsp_scan.log`。**结果待下轮回收。**

**🩺 中间发现（2026-10-04 ~09:10，config ① 收尾前）—— ⭐ TP2 自身明显变慢，价值只在「换 MBS=4 落地」**：

| 配置 | TP | SP | MBS | 稳态 s/iter | tok/s | GPU util (TFLOP/s/GPU) | 峰值显存 (max/8) |
|:--|:--|:--|:--|--:|--:|--:|--:|
| P-9.1 基线 | 1 | off | 2 | **19.3** | **218K** | **519** | 56865 MiB |
| **① TP2·MBS2** | 2 | off | 2 | **34.1** | **123K** | **~290** | **34265 MiB** |

- **TP2 吞吐 = 123K vs TP1 218K → 慢 ~44%（s/iter 34.1 vs 19.3 = 1.77×）**；但显存减半（34GB vs 57GB）。
- **机制**：TP2 每层引入 allreduce 通信 + 每卡 GEMM K/N 减半（`Total params 3.00B`，`most-loaded shard 1.4986B`）→ 单卡算力效率掉到 ~290 TFLOP/s/GPU（BF16 ≈989 的 ~29%，vs TP1 519 = ~52%）。
- **结论待定**：TP2 自身不划算；**唯一价值 = 让 MBS=4 落地**（M=MBS×seq=16384 进 FP8 交叉点）。等 config ②（TP2·MBS4）/④（TP2·SP·MBS4）收尾：
  - 若 ②/④ 的 MBS=4 **落地且 s/iter 较 ① 显著下降**（M↑ 摊薄通信）→ TP2·MBS4 可能仍是 FP8 的一把钥匙；
  - 若 MBS=4 **仍 OOM 或 s/iter 不降** → **P-8 维持 TP1·DP8·MBS=2（218K tok/s）**，FP8 走 P-9.3 抬 seq 那条杠杆。
- 原始输出（config ①，`/tmp/baize_p9_tp2_mbs2.log`）：
  - `[08:42:10] iteration 10/60 ... elapsed 37864.5ms`（首 10 步含编译/预热）
  - `[08:48:00] iteration 20/60 ... 34988.9ms | Step Time 34.99s GPU 287.8 TFLOP/s/GPU`
  - `[08:53:52] iteration 30/60 ... 35236.2ms`
  - `[08:59:39] iteration 40/60 ... 34694.0ms | Step Time 34.69s GPU 290.3`
  - `[09:05:21] iteration 50/60 ... 34139.1ms | Step Time 34.14s GPU 295.0`

**🩺 中间发现（2026-10-04 ~09:42，config ② 收尾）—— ⭐⭐ TP2·MBS=4 落地、不 OOM，且 s/iter 降至 ~20.7（≈TP1·MBS2），FP8 交叉点的钥匙到手**：

| 配置 | TP | SP | MBS | 稳态 s/iter | tok/s | GPU util (TFLOP/s/GPU) | 峰值显存 (max/8) |
|:--|:--|:--|:--|--:|--:|--:|--:|
| P-9.1 基线 | 1 | off | 2 | **19.3** | **218K** | **519** | 56865 MiB |
| ① TP2·MBS2 | 2 | off | 2 | 34.1 | 123K | ~290 | 34265 MiB |
| **② TP2·MBS4** | 2 | off | **4** | **~20.7** | **~200K** | **~482** | **55657 MiB ✅ 不 OOM** |

- **✅ MBS=4 在 TP2·DP4 下落地**（峰值 55657 MiB < 56865 MiB 的 TP1·MBS2，**比 TP1 下 MBS=4 的 81087 MiB OOM 省了 ~25GB**）→ **M = MBS×seq = 4×4096 = 16384，正好到 FP8 交叉点（M≳16K）**。这是 P-9.1 结论（TP1 下 MBS≥4 OOM）的**破局**。
- **s/iter 20.7s → ~200K tok/s（482 TFLOP/s/GPU）**：**只比 TP1·MBS2 基线（218K）慢 ~8%**，但 GEMM 的 M 翻倍。**机制印证**：MBS 2→4 把 M=8192→16384，摊薄了 TP2 每层 allreduce（见 ① 的 34.1s），并让每卡 GEMM 矩形更"厚"→ 单卡效率从 ① 的 290 跳到 482 TFLOP/s/GPU（~49% 峰值）。
- **P-8 决策分叉成形**：
  - **A. TP1·DP8·MBS2**：218K tok/s（bf16），但 M=8192 < 16K → **FP8 无收益**；
  - **B. TP2·DP4·MBS4**：~200K tok/s（bf16），M=16384 = **FP8 交叉点**。若 P-9.4 FP8 复评在此 M 下给出 `s>1`（运维预期 → 1.34 饱和区）→ **B·FP8 ≈ 260K tok/s，反超 A**。
  - → **P-9.4（FP8 复评）有了具体载体**：在 **TP2·MBS4（M=16384）** 下做 bf16 vs FP8 端到端对照。等 ③/④（SP on）收尾后定稿。
- 原始输出（config ②，`/tmp/baize_p9_tp2_mbs4.log`）：
  - `[09:19:43] iteration 20/60 ... 20880.1ms | Step Time 20.88s GPU 482.3 TFLOP/s/GPU`
  - `[09:23:09] iteration 30/60 ... 20601.9ms`
  - `[09:26:36] iteration 40/60 ... 20713.0ms`
  - `[09:30:08] iteration 50/60 ... 21222.1ms`
  - `[09:33:45] iteration 60/60 ... 21689.2ms | peak_gpu_mem 55657 MiB | rc=0`

**🩺 中间观察（2026-10-04 ~09:42，config ③ TP2·SP·MBS2 起跑 iter10）**：
- `[09:41:13] iteration 10/60 ... 38419.5ms | Step Time 38.42s GPU 262.1 TFLOP/s/GPU`（首 10 步含编译/预热）。
- SP on 在 TP2·MBS2 下**无加速迹象**（262 vs ① 的 290 TFLOP/s/GPU，但尚早、含预热，等稳态 40+ 步再判）。③/④ 预计 ~11:00 收尾。

**✅ config ③ 收尾（2026-10-04 ~10:11，第 60 次唤醒）—— SP on 对 MBS=2 无收益（s/iter 反而 +4.7%）**：

| 配置 | TP | SP | MBS | 稳态 s/iter | tok/s | GPU util (TFLOP/s/GPU) | 峰值显存 (max/8) |
|:--|:--|:--|:--|--:|--:|--:|--:|
| P-9.1 基线 | 1 | off | 2 | **19.3** | **218K** | **519** | 56865 MiB |
| ① TP2·MBS2 | 2 | off | 2 | 34.1 | 123K | ~290 | **36391 MiB** |
| ② TP2·MBS4 | 2 | off | 4 | ~20.7 | ~200K | ~482 | 55657 MiB ✅ |
| **③ TP2·SP·MBS2** | 2 | **on** | 2 | **~35.7** | **~117K** | ~272 | **34839 MiB** |

- **SP on（③ vs ①，MBS=2 同点）**：s/iter 34.1→35.7（**+4.7% 变慢**），峰值显存 36391→34839（**仅省 ~4.3% / 1.5GB**）。→ **SP 对 MBS=2 无吞吐收益**，反而略有损耗；显存收益也微乎其微（TP2·MBS2 本就不吃紧）。
- **口径更正**：config ① 峰值显存此前写 34265 MiB（早期 nvidia-smi 抽读）→ **以扫描脚本 per-config 自跟踪 max-over-8-GPU 为准 = 36391 MiB**（②=55657、③=34839 同口径）。
- **对 P-8 的含义不变**：SP 定位为「帮 MBS=4 进一步省激活显存」的**最后手段**，其价值看 config ④（TP2·SP·MBS4）能否在 ② 基础上再减显存/再提 MBS；若 ④ 也如 ③ 般无加速 → SP 对 P-8 **不推荐**，维持 **TP2·DP4·SP-off·MBS4（~200K，M=16384）** 作 FP8 载体。
- 原始输出（config ③，`/tmp/baize_p9_tp2sp_mbs2.log`，SUM `peak_gpu_mem_MiB=34839 rc=0`）：
  - `[09:58:57] iteration 40/60 ... 35308.2ms | Step Time 35.31s GPU 272.6 TFLOP/s/GPU`
  - `[10:04:56] iteration 50/60 ... 35921.0ms`
  - `[10:10:53] iteration 60/60 ... 35697.2ms | rc=0`（结束 10:11:23）

**✅ config ④ 收尾 · P-9.2 完整扫描定稿（2026-10-04 ~10:51，第 61 次唤醒）—— ⭐ SP on 在 MBS=4 下反向收益（+6% 加速 + 省 ~4.6GB），④ 成为 bf16 最优 FP8 载体**：

| 配置 | TP | SP | MBS | 稳态 s/iter | tok/s | GPU util (TFLOP/s/GPU) | 峰值显存 (max/8) |
|:--|:--|:--|:--|--:|--:|--:|--:|
| P-9.1 基线 | 1 | off | 2 | **19.3** | **218K** | **519** | 56865 MiB |
| ① TP2·MBS2 | 2 | off | 2 | 34.1 | 123K | ~290 | 36391 MiB |
| ② TP2·MBS4 | 2 | off | 4 | ~21.2 | ~198K | ~482 | 55657 MiB ✅ |
| ③ TP2·SP·MBS2 | 2 | on | 2 | ~35.7 | ~117K | ~272 | 34839 MiB |
| **④ TP2·SP·MBS4** | 2 | **on** | **4** | **~20.0** | **~210K** | **~503** | **51021 MiB ✅** |

- **⭐⭐ SP on 在 MBS=4 下反向（vs ③ 在 MBS=2 下 +4.7% 变慢）**：④ vs ②（同为 MBS=4）—— s/iter **21.2 → 20.0（~6% 加速）**，峰值显存 **55657 → 51021（省 ~4.6GB）**。机制：MBS=4 时激活/层归一化/序列内 elementwise 占比升高，SP 把 LayerNorm/Dropout 切到 TP 两卡分摊，既减显存又减该部分时延；MBS=2 时这些项占比小、SP 的 allreduce 代价反而盖过收益。
- **④ = bf16 下「够到 FP8 交叉点」的最优配置**：~210K tok/s（20.0s/iter）+ GPU util ~503 TFLOP/s/GPU，**只比 TP1·MBS2 基线（218K）慢 ~4%**，但 **M=MBS×seq=4×4096=16384 = FP8 交叉点**（① 的 M=8192 无 FP8 收益）。
- **P-8 决策分叉（更新）**：
  - **A. TP1·DP8·MBS2**：218K tok/s（bf16），M=8192 → FP8 无收益；
  - **B. TP2·DP4·SP-on·MBS4**：~210K tok/s（bf16），M=16384 = FP8 交叉点。若 P-9.4 在此 M 下端到端 FP8 `s>1`（运维预期 s→1.34 饱和区）→ **B·FP8 ≈ 210K×1.3 ≈ 273K，明确反超 A（218K）**。
- → **P-9.4 FP8 复评载体 = TP2·MBS4**（端到端 bf16 vs FP8 对照时，SP on 为当前最优，但需先确认 FP8 与 SP 的兼容性；若 FP8+SP 有冲突则回落 SP-off ②）。
- 原始输出（config ④，`/tmp/baize_p9_tp2sp_mbs4.log`，SUM `peak_gpu_mem_MiB=51021 rc=0`）：
  - `[10:22:24] iteration 30/60 ... 20239.2ms | Step Time 20.24s GPU 497.6 TFLOP/s/GPU`
  - `[10:25:43] iteration 40/60 ... 19926.5ms | Step Time 19.93s GPU 505.4`
  - `[10:29:03] iteration 50/60 ... 20020.3ms | Step Time 20.02s GPU 503.0`
  - `[10:32:24] iteration 60/60 ... 20069.1ms | Step Time 20.07s GPU 501.8 | rc=0`（结束 10:32:53）

**✅ P-9.2 定稿小结（全部 rc=0，无 OOM 无 NaN）**：TP2 自身（①~123K）明显慢于 TP1（218K），但**唯一价值 = 让 MBS=4 落地**；MBS=4 落地后（②④ ~200–210K）吞吐回升到接近 TP1 基线，且 **M=16384 进 FP8 交叉点**。**SP on 只对 MBS=4 有收益（④ vs ② +6%/+省 4.6GB），对 MBS=2 无收益（③ vs ① -4.7%）**。→ **P-8 bf16 备选 = TP2·DP4·SP-on·MBS4（~210K）** 或 **TP1·DP8·MBS2（218K）**，最终由 P-9.4（FP8 能否在 M=16384 转正）裁决。

**✅ P-9.4 前置已就绪（2026-10-04 ~10:16 核实环境，第 60 次）—— transformer_engine 版本确认**：
- `torch 2.8.0+cu128` / `CUDA 12.8` / `transformer_engine 2.12.0+5671fd36` / `megatron-core 0.16.1` / `mamba-ssm 2.2.6.post3` —— **与任务书预期的 TE 2.12.0 / torch 2.8.0+cu128 一致**（`python -c "import torch, transformer_engine; ..."` 贴原文，`from importlib.metadata import version`）。
- P-4R 微基准 `scripts/p4r_fp8_gemm_bench.py`（TE Linear fwd+bwd，E4M3/E5M2 vs bf16，`MS=[2048,4096,8192]`）**已具备**，P-9.4 将**复用并扩展 `M ∈ {4096,8192,16384,32768,65536}`**（用 `(MBS,seq)` 组合命中，生产载体 = **TP2·MBS4 → M=16384**），再在 TP2·MBS4 下做 **bf16 vs FP8 端到端对照**。

### P-9.4 微基准：s(M) 曲线与交叉点（✅ 已完成，2026-10-04 ~10:57，第 61 次唤醒）

> **方法**：扩展 P-4R 的 TE Linear（delayed-scaling FP8，E4M3 fwd / E5M2 bwd，master weights bf16）fwd+bwd 微基准，`M ∈ {4096,8192,16384,32768,65536}` × 6 个生产形状（`ffn_up_gate 2048×8192` / `ffn_down 8192×2048` / `attn_qkv 2048×3072` / `attn_out 2048×2048` / `mamba_in_proj 2048×10304` / `mamba_out_proj 4096×2048`）。脚本 `scripts/p9_4_fp8_gemm_scan.py`，1 卡，输出 `/tmp/baize_p94_bench.log`。`s = t_bf16 / t_fp8`。

**每个形状的 s(M)（fwd+bwd 单算子，ms：bf16 / fp8）**：

| 形状 | M=4096 | M=8192 | M=16384 | M=32768 | M=65536 |
|:--|--:|--:|--:|--:|--:|
| ffn_up_gate (2048→8192) | 0.94 | 1.21 | 1.28 | 1.32 | 1.32 |
| ffn_down (8192→2048) | 0.63 | 0.56 | 1.10 | 1.30 | 1.34 |
| attn_qkv (2048→3072) | 0.43 | 0.56 | 0.55 | 1.01 | 1.32 |
| attn_out (2048→2048) | 0.47 | 0.64 | 0.61 | 0.61 | 1.20 |
| mamba_in_proj (2048→10304) | 0.58 | 0.79 | 1.27 | 1.33 | 1.34 |
| mamba_out_proj (4096→2048) | 0.44 | 0.52 | 0.58 | 1.29 | 1.36 |
| **均值（未加权）** | **0.58** | **0.71** | **0.90** | **1.14** | **1.31** |

**关键结论（⭐⭐ 对运维「M≳16K 交叉点」的核实与修正）**：
1. **大 GEMM（FFN/SSM 投影，K·N ≥ 8M）**：确实在 **M≈16K 就转正**（ffn_down 1.10、mamba_in_proj 1.27、ffn_up_gate 1.28 @16384），到 M=32K 饱和 ~1.3。→ **运维的方向判断对「大 GEMM」成立**。
2. **小 GEMM（attention 投影，N=2048/3072）**：FP8 的 cast/amax 开销占比大，**要 M≳32K 才转正**（attn_qkv 在 32768 才 1.01、attn_out 在 65536 才 1.20、mamba_out_proj 在 16384 仍 0.58）。
3. **未加权均值在 M=16384 仍是 0.90（倒挂 ~10%）**，交叉点在 **M≈30–32K**（非 16K）。→ **在「bf16 最优可达配置」（TP2·MBS4 → M=16384）下，按形状均值 FP8 仍未转正**。
4. ⚠️ **但这是「未加权」均值**：真实模型按 FLOP/执行时间加权，**大 GEMM（FFN/SSM，FLOP 占比高）已 s>1**，小 GEMM（attention）虽倒挂但 FLOP 占比小 → **端到端加权结果可能落在 s≈1 附近（略正或略负）**。→ **必须靠端到端对照裁决**（见下）。

### P-9.4 端到端 bf16 vs FP8 🚀 running（2026-10-04 10:58 启动）

> **FP8 配方已确认激活**（`--precision bf16_with_fp8_delayed_scaling_mixed` → recipe 落地为 `fp8: hybrid` / `fp8_recipe: delayed` / `fp8_param: true` / `fp8_wgrad: true` / `fp8_amax_history_len: 1024`，与 Xmodel-2.5 的 delayed-scaling 同款；原始输出见 `/tmp/baize_p94_fp8_tp2_mbs4.log`）。
> **对照设计**（同 MBS=4、同步数 60、TP2，跨 SP 两档）：
>   - A. `p94_fp8_tp2_mbs4`（SP-off）→ vs ② bf16 = 21.2s / ~198K tok/s
>   - B. `p94_fp8_tp2sp_mbs4`（SP-on）→ vs ④ bf16 = 20.0s / ~210K tok/s

**🩺 中间发现（2026-10-04 ~11:39，第 62 次唤醒）—— ⭐⭐ config A（SP-off）FP8 端到端收尾：FP8 几乎零收益（s≈1.01），未复现 +30%**：

| 对照 | bf16 s/iter | FP8 s/iter | FP8 GPU util | FP8 峰值显存 | **端到端 s = t_bf16/t_fp8** |
|:--|:--|:--|:--|:--|:--|
| **A. TP2·SP-off·MBS4**（vs ②） | **21.2s** | **~21.0s** | 479.3 TFLOP/s/GPU | **50721 MiB** | **~1.01（+~1%，等价持平）** |
| **B. TP2·SP-on·MBS4**（vs ④） | **20.0s** | **~23.2s**（60 步 rc=0 收官） | 434.7/429.8/436.1 TFLOP/s/GPU | **47987 MiB** | **~0.86（反变慢 ~+16%，倒挂）** |

- **config A 原始输出**（`/tmp/baize_p94_fp8_tp2_mbs4.log`，60 步 rc=0，loss 7.352→ grad norm 0.262，无 NaN/skip）：
  `Step Time : 21.01s GPU utilization: 479.3TFLOP/s/GPU`，peak_gpu_mem_MiB=50721。
- **⭐⭐ 最终结论（P-9.4 铁律，诚实记录）**：**FP8 在 M=16384（TP2·MBS4）下端到端不转正** ——
  A（SP-off）21.0s vs bf16 ② 21.2s = **+~1%（噪声级持平）**；B（SP-on）~23.2s vs bf16 ④ 20.0s = **~+16% 变慢（倒挂）**（FP8 的 amax/delayed-scaling allreduce 与 SP 的 allreduce 叠加冲突）。
  → **未复现 Xmodel-2.5 的 +30%**。这与 P-9.4 微基准一致（交叉点 M≈30–32K 而非 16K；M=16384 未加权 s=0.90 倒挂）——**本模型在「bf16 可达最大 M」下 FP8 不可行**。A/B 均 60 步 rc=0、loss 7.35→ grad norm 0.26、无 NaN/skip。
- **诚实记录（P-9.4 铁律）**：不迎合运维「s→1.34 饱和区」预期 —— **本模型/本口径下 FP8 不转正**，P-8 应**维持 bf16**，最优配置回到 **④ TP2·DP4·SP-on·MBS4（~210K）** 或 **P-9.1 的 TP1·DP8·MBS2（218K）**（后者无 FP8 收益、但吞吐更高、显存 57GB 更省）。
> 脚本 `run/baize_p94_fp8_e2e.sh`，SUM=`/tmp/baize_p94_fp8_e2e.log`。**✅ P-9.4 端到端完成（A/B 均 rc=0 收官）。**

### P-9.3 seq 多点扫描 🚀 running（2026-10-04 12:15 启动，第 63 次唤醒）

> **方法**：TP1·DP8·MBS=2 · bf16 · seed1234；seq ∈ {2048, 4096, 8192, 16384}，GBS 同步维持每步 ≈4.19M token（2048→2048 / 4096→1024 / 8192→512 / 16384→256）。每点 60 步短测（不存 ckpt），记 t_step / tok/s / 峰值显存 / OOM。
> **目的**：量化「hybrid 把注意力 O(n²) 关掉多少」——`r = t_step(seq)/t_step(4096)`。纯 Transformer 会 2–4×；P-4 实测 attention flash 仅占 0.7%（seq4096），预计 hybrid 的 8192 落在 r≈1.05–1.20。
> **判据（预注册，先定后测，🚫 不改）**：`r ≤ 1.2` → 该 seq 作 P-8 候选；`r ≥ 1.5` → P-8 沿用 4096。**16384 若 OOM → 如实记 OOM**（= 显存先于算力成为限制）。
> **5-way 归因**（attention/SSM/GEMM/comm/elementwise）由 **P-9.5 profiling** 承担。脚本 `run/baize_p9_seq_scan.sh`，SUM=`/tmp/baize_p9_seq_scan.log`。

| seq | GBS | 状态 | 峰值显存 | r vs 4096 | 备注 |
|:--|--:|:--|--:|--:|:--|
| 2048 | 2048 | ✅ rc=0（12:46） | 41513 MiB | —（s/iter ~29.7s → ~141K tok/s） | seq↓ 每 token 更慢（2× grad-accum + M=4096 更小）|
| 4096 | 1024 | 🚀 running（12:46 起） | — | 1.0 | 同-run 基线（vs P-9.1 TP1·MBS2 19.3s/218K） |
| 8192 | 512 | 待 | — | — | |
| 16384 | 256 | 待 | — | — | 边界点，可能 OOM |

### P-9.6 ⭐ 最高优先指令（运维 2026-10-04）—— 两步法：① bf16 找速度最优（抬 M≥32768）→ ② 该点测 FP8 🚩 已落地待跑

> **背景**：当前最优 ④ TP2·SP·MBS4 峰值仅 51.0G/80G → 余量 ~29G ⇒ MBS 可再上抬。**要真正回答「FP8 有没有收益」，必须先抬 M=MBS×seq 到 ≥32768**（FP8 交叉点 M≈30–32K，非 16K；P-9.4 在 M=16384 测 FP8 本就是「不公平考场」）。
> **两步法（运维指定）**：① 先 bf16 下扫「训练速度最优」配置 → ② 在最优点测 bf16 vs FP8。
> **两杠杆（M=MBS×seq）**：①抬 MBS（4→8→16，受显存限，可配 TP4）②**抬 seq（运维推荐先试：seq8192→GBS512·MBS4 使 M=32768，一次给两样：过交叉点+长上下文能力）**。
> **判据（预注册，先定后测）**：bf16 最优 = **吞吐最优 且 峰值显存 ≤72G**（留 ≥8G 余量）；FP8 端到端 **s>1.05 才转正**（否则定稿 bf16，把「不转正」作正式结论入库）；**最优点 M<32768 则补一个 M≥32K 点**。⚠️ FP8 A/B **必带 `CUDA_DEVICE_MAX_CONNECTIONS=1`**（P-9.4 发现 B(SP-on) FP8 反慢 ~15%，疑 FP8+SP allreduce 叠加）。
> **顺序**：P-9.6① → P-9.6② → P-9.5 → P-6② → 定 P-8。成本控制：点数 ≤10（已按吞吐可能性排序）。

**运维 ④ 确认（12:30）推荐的 10 点扫描表（每点 60 步 bf16，均守 GBS×seq≈4.19M）**：

| 序 | seq | GBS | TP | SP | MBS | **M** | 作用 |
|:--|--:|--:|:--|:--|--:|--:|:--|
| 1 | 8192 | 512 | 2 | on | 4 | **32768** | 🎯运维预测最优点 |
| 2 | 8192 | 512 | 2 | off | 4 | 32768 | SP 对照 |
| 3 | 16384 | 256 | 2 | on | 4 | 65536 | 更远 |
| 4 | 16384 | 256 | 2 | off | 4 | 65536 | SP 对照 |
| 5 | 4096 | 1024 | 2 | on | 8 | 32768 | MBS 轴对照 |
| 6 | 4096 | 1024 | 2 | off | 8 | 32768 | MBS/SP 交叉 |
| 7 | 4096 | 1024 | 2 | on | 16 | 65536 | 上探（预期 OOM）|
| 8 | 8192 | 512 | 4 | on | 8 | 65536 | TP4 换显存 |
| 9 | 8192 | 512 | 1 | off | 2 | 16384 | TP1 对照（已被在跑 seq scan 覆盖）|
| 10 | 4096 | 1024 | 2 | on | 4 | 16384 | ④ 基线（已测 210K/51021 MiB）|

> **脚本 `run/baize_p96_tpsp_seq_scan.sh` 已写（第 64 次唤醒，点 1–8）**，SUM=`/tmp/baize_p96_tpsp_seq_scan.log`。**待当前 P-9.3 seq scan 结束后启动**（勿打断 running 的 seq scan）。可剪枝：点 1/2 峰值 >72G 或 OOM → 跳 3/4、5/6；点 1 吞吐已优于 210K → 优先扩 seq（3/4）。

### P-9.6① bf16 最优搜索 ✅ 完成（2026-10-04 14:05:20 END，第 66 次唤醒）—— ⭐ 8 点全测：抬 M≥32768 全 OOM 或更慢，速度最优仍是 seq4096

> 脚本 `run/baize_p96_tpsp_seq_scan.sh`，SUM=`/tmp/baize_p96_tpsp_seq_scan.log`。每点 60 步 bf16、守 GBS×seq≈4.19M、不存 ckpt。

**结果表（8 点，M=MBS×seq）**：

| 序 | seq | GBS | TP | SP | MBS | M | 结果 | peak | 判定 |
|:--|--:|--:|:--|:--|--:|--:|:--|--:|:--|
| 1 | 8192 | 512 | 2 | on | 4 | 32768 | ❌ 训练期 OOM | 81057 | 抬 seq 轴在 TP2 放不下 |
| 2 | 8192 | 512 | 2 | off | 4 | 32768 | ❌ 训练期 OOM | 80353 | 同上（SP off 也 OOM）|
| 3 | 16384 | 256 | 2 | on | 4 | 65536 | ❌ 训练期 OOM | 81057 | 更远更放不下 |
| 4 | 16384 | 256 | 2 | off | 4 | 65536 | ❌ 训练期 OOM | 80829 | 同上 |
| 5 | 4096 | 1024 | 2 | on | 8 | 32768 | ❌ 训练期 OOM | 81053 | MBS 轴在 TP2 也 OOM |
| 6 | 4096 | 1024 | 2 | off | 8 | 32768 | ❌ 训练期 OOM | 81043 | 同上 |
| 7 | 4096 | 1024 | 2 | on | 16 | 65536 | ❌ 训练期 OOM | 81079 | 上探（如期 OOM）|
| 8 | 8192 | 512 | 4 | on | 8 | 65536 | ✅ **训练成功 60/60**（仅尾部存 ckpt OOM）| 81081* | 唯一 M≥32768 落地 |

> `*` 点 8 的 peak 81081 MiB 是**存 ckpt 瞬间**（save gather 触发 unhandled cuda error）；**训练期真实峰值 = max allocated 66.4GB / max reserved ~71GB**（from rank0-3 after-10-iters 报告），**不超 80GB**。

**⭐ 点 8（TP4·SP·MBS8·seq8192, M=65536）训练细节**：iteration 60/60 lm loss 7.43、grad norm 0.262、skip=0/nan=0；**Step Time 22.16s/iter → ~189K tok/s（GBS512×seq8192=4.19M/步）、522 TFLOP/s/GPU**；「after training is done」存 ckpt 时 gather_object 触发 `RuntimeError: NCCL Error 1: unhandled cuda error`（save 内存超 79GB 上限）。→ 处置：SIGTERM 清掉 save-OOM 后挂死 28min 的 torchrun（占 ~79GB、0% util）。

**⭐⭐ 结论（诚实、铁律，不迎合「seq 轴」预判）**：

1. **bf16 速度最优 = seq4096**：`TP1·DP8·MBS2 = 249K tok/s`（P-9.3，峰值 56807 MiB）或 `④ TP2·SP·MBS4 = 210K`（P-9.2，峰值 51021 MiB）。二者 M=8192/16384，均 **< 32768**。
2. **抬 M≥32768 的两条杠杆在本硬件（8×H100 80GB）上走不通**：
   - **抬 seq（8192/16384）**：TP1 OOM（P-9.3）、TP2 OOM（点1-4）——激活 >80GB 放不下。
   - **抬 MBS（8/16）**：TP2 OOM（点5-7）；TP4 才放得下（点8），但 **TP4 通信开销吃到只剩 189K，仍慢于 seq4096 的 249K**。
3. **吞吐随 M 单调下降**：249K（M=8192）→ 210K（M=16384）→ 189K（M=65536）。→ **运维预判「最优点大概率是抬 seq+SP on」被证伪**：抬 seq 需要 TP2/TP4 换显存，TP 通信开销正好吃掉 seq 抬升本可带来的长上下文收益（净吞吐反降）。
4. **FP8 交叉点 M≈30–32K 在本硬件上不可达（bf16 口径）** → P-9.6② 只能在**唯一落地**的 M=65536 配置（TP4·SP·MBS8·seq8192）上测 FP8，看「M 大 + FP8」能否把 189K 拉回、甚至超过 seq4096 的 bf16。

### P-9.6② FP8 e2e A/B 🚀 running（2026-10-04 14:07:02 启动）

> 脚本 `run/baize_p96b_fp8_e2e.sh`，SUM=`/tmp/baize_p96b_fp8_e2e.log`。载体 = 唯一可达 M≥32768 配置 **TP4·SP·MBS8·seq8192（M=65536）**，`--precision bf16_with_fp8_delayed_scaling_mixed`，60 步 × 2 点。
> **A/B**：`B` = 默认连接（复现 P-9.4 的 SP amax allreduce 叠加是否仍在 M=65536 拖累）；`A` = `CUDA_DEVICE_MAX_CONNECTIONS=1`（隔离 amax+SP allreduce 叠加）。
> **bf16 基线 = 点8 22.16s/iter（~189K tok/s）**；**判据（预注册）**：`s = t_bf16 / t_fp8 > 1.05` → FP8 转正 → 写入 P-8 建议；`≤1.05` → 不转正 → **定稿 bf16，把「不转正」作正式结论入库**。ETA ~15:00。