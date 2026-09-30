# EXPERIMENTS_PRETRAIN_2B.md — BaiZe Stage(i) Mamba2-hybrid 2B 预训练超参搜索实验记录

> 骨架固定：Mamba2-hybrid（56 层 Nemotron-H 式顺序混合，**2.220B** 真实参数量）。
> 固定口径（跨配置一致）：8 卡（10.239.2.29，TP1/DP8）/ GBS=8 / mb=1 / seq=4094 / bf16 / AdamW(β1=0.9 β2=0.95 eps=1e-5 wd=0.1) / seed=1234 / eval 关闭（eval_iters=0）。
> 数据：`data/ultrafineweb_l3_qa`（200k docs / 164.75M token），总样本 40243（seq4094）。
> 短地平线 5000 步/组 ≈ 164M token；长跑 S5-01 20000 步（需补切 ≥700M token）。

## 胜出配置（✅ S2/S3/S4/S5 全定 converged：stable LR=1e-3 / 调度族 WSD / warmup=250 / decay=500 / min_lr=1e-5 / 退火数据混合 **L3+code+math 86:10:4**）

- 🔑 **S2 stable LR 胜出 = `1e-3`（final loss 2.7627 @5000）**：7 点随 LR 单调递减 2e-4(2.9037)→3e-4(2.8462)→4e-4(2.8167)→5e-4(2.7981)→6e-4(2.7783)→8e-4(2.7700)→**1e-3(2.7627)**，退火尾段 2.92@4440→2.76@5000 骤降，1e-3 反超 8e-4 成为最低。
- ⚠️ **边界提示**：7 点 loss 随 LR 单调递减止于网格上限 1e-3，最优 LR 可能 ≥1e-3，S3 后可增量扫 1.2e-3/1.5e-3（余预算 ~100 GPU·h 允许）。
- ✅ S3 关键轴全定（在 1e-3 上单变量，5 点全回收）：S3-01 WSD参考✅2.767915 / S3-02 cosine✅2.815509（**WSD 胜 cosine** 差~0.048）/ S3-03 decay5%✅2.789989（**decay10% 胜 5%**）/ S3-04 warmup2000✅2.795710（**warmup250 胜 2000** 差~0.028）/ S3-05 min_lr1e-5✅**2.764702**（**1e-5 胜 3e-5**：2.764702 vs 2.767915，Δ~0.003 略优，处 run-to-run 噪声 ~0.005 内，取更低点估计）。
- 🎯 **胜出配置（S1–S3 全定）**：`stable LR=1e-3` `/` `调度族=WSD` `/` `warmup=5%(250)` `/` `decay=10%(500)` `/` `min_lr=1e-5`；固定口径 GBS=8/mb=1/seq=4094/bf16/AdamW(β1=.9 β2=.95 eps=1e-5 wd=.1)/seed=1234。
- 🏆 **S4 退火数据混合胜出 = `L3+code+math 86:10:4`（final loss 2.629822 @5000）**：纯L3(2.762086) → L3+code 90:10(2.679322) → **L3+code+math 86:10:4(2.629822)** 阶梯式压降。⚠️ 需注意 code/math 源本身熵更低，loss 降幅含分布偏移成分（非纯「退火质量增益」，见论文 caveat）；短地平线用全段静态 blend 代理「decay 尾段混入」。
- ✅ **最终胜出配置（S1–S4 全定）**：`stable LR=1e-3` / `WSD` / `warmup=250` / `decay=500` / `min_lr=1e-5` / 退火混合 `L3(86%)+code(10%)+math(4%)`。
- 🏁 **S5 长跑 + 多 seed（converged，2026-09-30）**：胜出配置 20000 步长跑（seed1234）**final loss 2.205413 @20000**（decay 尾段 19500→20000 由 stable ~2.34 退火降至 2.205，退火增益 ~0.14）；3 seed × 5000 复现 **均值 2.673868 ± 0.0469（样本 σ，n=3）**（s5_02 seed44 2.640200 / s5_03 seed777 2.653915 / s5_04 seed2024 2.727488）；20000 步收敛曲线见 `s5_01_loss_curve.png`（2000 采样点，grad norm 0.194，无 NaN）。

## 可复现训练命令（胜出配置）

```bash
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230:$PYTHONPATH
conda activate py310
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027

# 短地平线（5000 步，多 seed 复现；seed 可换 44/777/2024）：
torchrun --nnodes=1 --nproc_per_node=8 --master_addr=127.0.0.1 --master_port=29691 \
  pretrain_launcher.py --arch mamba2 --name s5_rep --dir $PWD/nemo_experiments \
  --tokenizer-path $PWD/data/tokenizer_eod \
  --train-data-path 86 $PWD/data/ultrafineweb_l3_qa 10 $PWD/data/anneal_code 4 $PWD/data/anneal_math \
  --tensor-parallel 1 --train-iters 5000 --global-batch-size 8 --micro-batch-size 1 --seq-length 4094 \
  --eval-interval 250 --eval-iters 0 --lr 1e-3 --min-lr 1e-5 \
  --lr-warmup-iters 250 --lr-decay-iters 500 --lr-decay-style WSD --seed 1234 --precision bf16_mixed

# 长跑（20000 步，seed1234，论文收敛曲线；700m 主体 86% + code 10% + math2 4%）：
torchrun --nnodes=1 --nproc_per_node=8 --master_addr=127.0.0.1 --master_port=29691 \
  pretrain_launcher.py --arch mamba2 --name s5_01 --dir $PWD/nemo_experiments \
  --tokenizer-path $PWD/data/tokenizer_eod \
  --train-data-path 86 $PWD/data/ultrafineweb_l3_qa_700m 10 $PWD/data/anneal_code 4 $PWD/data/anneal_math2 \
  --tensor-parallel 1 --train-iters 20000 --global-batch-size 8 --micro-batch-size 1 --seq-length 4094 \
  --eval-interval 250 --eval-iters 0 --lr 1e-3 --min-lr 1e-5 \
  --lr-warmup-iters 250 --lr-decay-iters 500 --lr-decay-style WSD --seed 1234 --precision bf16_mixed
```

## 实验记录表
| ID | 阶段 | stable LR | 调度族 | decay/warmup/min_lr | 退火混合 | 状态 | val loss | 训练tok/s | 耗时 | GPU·h | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| S0-01 | S0 | — | WSD | — | — | ✅ done | — | ~99K | ~2.2min | ~0.3 | 8 卡冒烟 30 步，稳态 ~330ms/iter，loss 7.90@30，WSD 调度验证通过 |
| S1-01 | S1 | 3e-4 | WSD | 500/250/3e-5 | — | ✅ done | 2.849@5000 | ~99K(独占) | ~41min | ~5.5 | baseline 5000 步，loss 7.90@30→2.849@5000；⚠️ 被同行 vision 抢占 GPU0~5，step time 330→850ms，tok/s 基线下沉 |
| S2-01…S2-07 | S2 | 2e-4…1e-3 | WSD | 500/250/3e-5 | — | ✅ done | — | ~99K | ~26min/点 | ~25.4 | 7 点串行 sweep，**胜出 LR=1e-3（2.7627）**；明细见下方「S2 LR 扫描明细」 |
| S3-01…S3-05 | S3 | 1e-3 | 变 | 变 | — | ✅ done | — | — | ~27min/点 | ~18 | 1e-3 上单变量：s3_01 WSD参考✅(2.767915)、s3_02 cosine✅(2.815509，**WSD 胜 cosine**)、s3_03 decay5%✅(2.789989，**decay10%胜**)、s3_04 warmup2000✅(2.795710，**warmup250胜**)、s3_05 min_lr1e-5✅(**2.764702**，**1e-5 胜 3e-5**)；见下方「S3 关键轴明细」 |
| S4-01…S4-03 | S4 | 1e-3 | WSD | 500/250/1e-5 | 变 | ✅ done | — | ~99K | ~27min/组 | ~10.8 | s4_01 纯L3✅(2.762086)；s4_02 L3+code 90:10✅(2.679322)；s4_03 L3+code+math 86:10:4✅(**2.629822 胜出**)（静态 blend，短地平线代理）；见下方「S4 退火混合明细」 |
| S5-01…S5-04 | S5 | 1e-3 | WSD | 500/250/1e-5 | L3(86%)+code(10%)+math(4%) | ✅ done | — | ~99K | ~104min/长跑 | ~24.7 | 胜出配置复现：s5_02(seed44)✅2.640200；s5_03(seed777)✅2.653915；s5_04(seed2024)✅2.727488；s5_01(20000步)✅**2.205413**（3 seed 均值 2.6739±0.0469） |

## S0 冒烟实测（2026-09-30）
- 8×H100，TP1/DP8，30 步从零（seq4094/GBS8/mb1/bf16，WSD warmup3/decay3 仅冒烟用）。
- 稳态 **~330ms/iter** ≈ **~99K tok/s**；首 10 步均 12.6s/iter（首步 SSM 编译 + CUDA-graph 一次性）。
- loss：11.37(iter10) → 8.43(iter20) → **7.90(iter30)**；grad norm 2.98→1.35，无 NaN/skip。
- WSD 调度确认：LR 3e-4(stable) → 3e-5(decay 尾，min_lr)。
- ckpt `nemo_experiments/s0_smoke_8gpu/checkpoints/iter_0000030`（torch_dist）。
- 总样本 40243（seq4094）；5000 步需 40000，余 243（0.6% margin，偏紧，S1 观察）。

## S2 LR 扫描明细（WSD 固定，7 点 × 5000 步，8 卡 TP1/DP8）
| ID | stable LR | final loss@5000 | grad norm | skip/nan | 耗时 | GPU·h | 状态 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| S2-01 | 2e-4 | **2.9037** | 0.543 | 0/0 | ~28.8min | ~3.8 | ✅ done |
| S2-02 | 3e-4 | **2.8462** | 0.455 | 0/0 | ~27.1min | ~3.6 | ✅ done |
| S2-03 | 4e-4 | **2.8167** | 0.414 | 0/0 | ~26.8min | ~3.6 | ✅ done |
| S2-04 | 5e-4 | **2.7981** | 0.372 | 0/0 | ~27min | ~3.6 | ✅ done |
| S2-05 | 6e-4 | **2.7783** | 0.331 | 0/0 | ~27min | ~3.6 | ✅ done |
| S2-06 | 8e-4 | **2.7700** | 0.279 | 0/0 | ~26.7min | ~3.6 | ✅ done |
| S2-07 | 1e-3 | **2.7627**（最终，反超 8e-4） | 0.241 | 0/0 | ~27min | ~3.6 | ✅ done |

## S3 关键轴明细（1e-3 上单变量，5 点 × 5000 步，8 卡 TP1/DP8）
| ID | 单变量 | 调度族 | warmup/decay/min_lr | final loss@5000 | grad norm | skip/nan | 耗时 | GPU·h | 状态 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| S3-01 | WSD 参考 | WSD | 250/500/3e-5 | **2.767915** | 0.239 | 0/0 | ~26.8min | ~3.6 | ✅ done（**复现 S2-07 2.7627**，run-to-run 噪声 ~0.005 内一致，S3 组内基线成立）|
| S3-02 | cosine | cosine | 250/500/3e-5 | **2.815509** | 0.341 | 0/0 | ~26.9min | ~3.6 | ✅ done（WSD 参考 2.767915 vs cosine 2.815509，差 ~0.048，**WSD 胜 cosine**）|
| S3-03 | decay 5% | WSD | 250/250/3e-5 | **2.789989** | 0.237 | 0/0 | ~26.9min | ~3.6 | ✅ done（WSD 参考 2.767915 vs decay5% 2.789989，差 ~0.022，**decay 10% 胜 5%**）|
| S3-04 | warmup 固定 2000 | WSD | 2000/500/3e-5 | **2.795710** | 0.249 | 0/0 | ~26.9min | ~3.6 | ✅ done（WSD 参考 2.767915 vs warmup2000 2.795710，差 ~0.028，**warmup 5%=250 胜固定 2000**）|
| S3-05 | min_lr 1e-5 | WSD | 250/500/1e-5 | **2.764702** | 0.241 | 0/0 | ~26.7min | ~3.6 | ✅ done（**1e-5 胜 3e-5**：2.764702 vs 2.767915，Δ~0.003 略优，处 run-to-run 噪声 ~0.005 内，取更低点估计）|

## S4 退火数据混合明细（胜出配置 LR1e-3/WSD/warmup250/decay500/min1e-5，3 组 × 5000 步，8 卡 TP1/DP8）
| ID | 退火混合 | final loss@5000 | grad norm | skip/nan | 耗时 | GPU·h | 状态 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| S4-01 | 纯 L3（基线） | **2.762086** | 0.240 | 0/0 | ~27min | ~3.6 | ✅ done（与 S2-07 2.7627 / S3-05 2.764702 噪声 ~0.005 内一致，S4 组内基线成立）|
| S4-02 | L3+code 90:10 | **2.679322** | 0.254 | 0/0 | ~27min | ~3.6 | ✅ done（18:17:25→18:44:38，master_port=29682；较纯L3 2.762086 低 ~0.083，code 数据压降 final loss）|
| S4-03 | L3+code+math 86:10:4 | **2.629822** | 0.247 | 0/0 | ~27min | ~3.6 | ✅ done（**S4 胜出**：较纯L3 2.762086 低 ~0.132；18:44:38→19:11:57，master_port=29683）|

## S5 长跑 + 多 seed 明细（胜出配置 LR1e-3/WSD/warmup250/decay500/min1e-5 + 退火 L3+code+math 86:10:4，8 卡 TP1/DP8）
| ID | seed | 步数 | final loss | grad norm | skip/nan | 耗时 | GPU·h | 状态 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| S5-02 | 44 | 5000 | **2.640200** | 0.247 | 0/0 | ~27.3min | ~3.6 | ✅ done（19:14:49→19:42:01，step 280.6ms；与 S4-03 2.629822 同配置 seed44 vs 1234 噪声 ~0.010 内一致）|
| S5-03 | 777 | 5000 | **2.653915** | 0.250 | 0/0 | ~27.4min | ~3.6 | ✅ done（19:42:01→20:09:26，step 318.0ms；较 s5_02 2.640200 高 ~0.014，seed 间噪声）|
| S5-04 | 2024 | 5000 | **2.727488** | 0.245 | 0/0 | ~27.3min | ~3.6 | ✅ done（20:09:26→20:36:12，step 304.1ms；较 s5_02 2.640200 高 ~0.087，seed 间噪声偏大）|
| S5-01 | 1234 | 20000 | **2.205413** | 0.194 | 0/0 | ~104min | ~13.9 | ✅ done（20:36:12→22:20:19，论文收敛曲线；700m 主体 86% + code 10% + math2 4%，decay 尾段 19500→20000 由 ~2.34 降至 2.205，退火增益 ~0.14）|

> 多 seed 均值±σ（3/3 已回收）：s5_02(2.640200)/s5_03(2.653915)/s5_04(2.727488)，**均值 2.673868、样本 σ≈0.0469、极差 0.087**。⚠️ seed2024 明显偏高（较 seed44 +0.087），使 σ 从早前 2-seed 估计的 ~0.007 放大到 ~0.047，复现误差须如实报告。s5_01 长跑（20000 步 seed1234）**final 2.205413@20000** 为论文主收敛曲线（`s5_01_loss_curve.png`，2000 采样点），decay 尾段退火增益 ~0.14。✅ S5 全部完成，PHASE=converged。

## S5-01 数据补切（≥700M token ✅ 完成，2026-09-30 13:16）
- `preprocess_data.py --input-dir .../Ultra-FineWeb-L3/.../qa --output-prefix data/ultrafineweb_l3_qa_700m --max-docs 900000`。
- ✅ 完成：**900000 docs / 741,712,139 tokens（≈742M ≥ 700M 门限）**，产物 `data/ultrafineweb_l3_qa_700m.bin`(2.97GB)/`.idx`(18MB)/`.json`。S5-01（20000 步≈655M）数据就绪。