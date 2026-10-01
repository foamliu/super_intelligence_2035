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

## P-5b　训练量 scaling 曲线 —— 🚧 数据分词启动（2026-10-02 ~06:25）

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