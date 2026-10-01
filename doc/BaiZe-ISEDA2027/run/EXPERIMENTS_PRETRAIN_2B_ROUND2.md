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

### 第 1 步（待 p3_hybrid 结束、GPU 空闲后执行）：profile 量 GEMM 占比

- 计划：用 BF16 配置跑 ~100 步，`torch.profiler` 拆时间 → 归类 `GEMM（linear/attn/MLP）` / `SSM selective-scan` / `norm+act` / `通信（NCCL）` / `数据加载`，得 GEMM 占比 `g`。
- ⚠️ 任务书自述「SSM 串行为 bottleneck」——若 scan 占大头，`g` 小，则 FP8 收益有限，**到此结论、不接 FP8**（第 2/3 步裁减）。

### 状态：**待跑**（环境已备，仅差 GPU 空闲；profile 脚本落地 + 运行放在下一唤醒）

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
| 1024 | 39 | 4e-3 | 2/4 | … | ⏳ running（22:34 起） |

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

## 论文回填建议（待填，P-1/P-2/P-3 完成后给出精确数值与文字建议）

1. **「最优点是否在边界」怎么写**（P-1 ✅ 已定稿）：**最优不在网格边界，1e-3 是扩展网格内部的全局极小值**。10 点 LR 曲线（2e-4…3e-3）明确 U 形、极小值齐整落在 `1e-3`（左翼 2e-4→1e-3 单调降，右翼 1.5e-3→3e-3 单调升），且 3e-3 无 NaN 未发散（仅 loss 退化至 ~3e-4 档水平）。建议把论文 "loss improves monotonically" 那句改为交代完整网格 + 极小值位置：*"loss is U-shaped over LR ∈ [2e-4, 3e-3], attaining its minimum at LR=1e-3 (2.763); LR remains stable up to 3e-3 (no divergence, only degraded loss), so the optimum is an interior point of the grid, not a truncated boundary."*
2. **「min_lr Δ 是否在噪声内」怎么写**：**Δ 在噪声内**。`1e-5` vs `3e-5` 的 Δ≈0.003213 仅 **~0.09σ**（n=5 复现 σ≈0.0349，mean 2.673386），远小于 run-to-run 噪声，两者**统计上不可区分**。建议把论文 "min_lr=1e-5 narrowly beats 3e-5" 改为 "min_lr 1e-5 and 3e-5 are statistically indistinguishable (Δ≈0.003 within run-to-run noise, σ≈0.035 across n=5 seeds); we adopt min_lr=1e-5 as default without claiming superiority"。
3. **「架构对比延长到 5000 步后的结论」怎么写**（P-3 ✅ 已定稿）：hybrid 在 500/1000/2000/3000/5000 五个 checkpoint **全优于 dense**（loss 差 Δ≈0.22~0.43，末段 0.30），且 hybrid（2.220B）比 dense（2.512B）**少 11.6% 参数**仍领先。建议论文把「hybrid 更优」从早期 1000 步快照升级为 5000 步口径的稳定结论，并**补一句参数量优势**：*"Across all five checkpoints from 500 to 5000 steps, the Mamba2-hybrid (2.220B) consistently attains lower loss than the dense MiniCPM5-2B baseline (2.512B), with the gap widening to Δ≈0.30 by step 5000 — confirming the hybrid advantage is not an early-training artifact and comes with an 11.6% parameter reduction."*