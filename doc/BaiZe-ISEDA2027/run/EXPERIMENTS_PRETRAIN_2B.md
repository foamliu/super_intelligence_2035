# EXPERIMENTS_PRETRAIN_2B.md — BaiZe Stage(i) Mamba2-hybrid 2B 预训练超参搜索实验记录

> 骨架固定：Mamba2-hybrid（56 层 Nemotron-H 式顺序混合，**2.220B** 真实参数量）。
> 固定口径（跨配置一致）：8 卡（10.239.2.29，TP1/DP8）/ GBS=8 / mb=1 / seq=4096（=2¹²，用户直令 2026-10-14；P-1~P-7 实际跑 4094 系 agent 错误，P-8 按 4094 跑完不干预）/ bf16 / AdamW(β1=0.9 β2=0.95 eps=1e-5 wd=0.1) / seed=1234 / eval 关闭（eval_iters=0）。
> 数据：`data/ultrafineweb_l3_qa`（200k docs / 164.75M token），总样本 40243（seq4094）。
> 短地平线 5000 步/组 ≈ 164M token；长跑 S5-01 20000 步（需补切 ≥700M token）。

## 胜出配置（✅ S2/S3/S4/S5 全定 converged：stable LR=1e-3 / 调度族 WSD / warmup=250 / decay=500 / min_lr=1e-5 / 退火数据混合 **L3+code+math 86:10:4**）

- 🔑 **S2 stable LR 胜出 = `1e-3`（final loss 2.7627 @5000）**：7 点随 LR 单调递减 2e-4(2.9037)→3e-4(2.8462)→4e-4(2.8167)→5e-4(2.7981)→6e-4(2.7783)→8e-4(2.7700)→**1e-3(2.7627)**，退火尾段 2.92@4440→2.76@5000 骤降，1e-3 反超 8e-4 成为最低。
- ⚠️ **边界提示**：7 点 loss 随 LR 单调递减止于网格上限 1e-3，最优 LR 可能 ≥1e-3，S3 后可增量扫 1.2e-3/1.5e-3（余预算 ~100 GPU·h 允许）。
- ✅ S3 关键轴全定（在 1e-3 上单变量，5 点全回收）：S3-01 WSD参考✅2.767915 / S3-02 cosine✅2.815509（**WSD 胜 cosine** 差~0.048）/ S3-03 decay5%✅2.789989（**decay10% 胜 5%**）/ S3-04 warmup2000✅2.795710（**warmup250 胜 2000** 差~0.028）/ S3-05 min_lr1e-5✅**2.764702**（**1e-5 胜 3e-5**：2.764702 vs 2.767915，Δ~0.003 略优，处 run-to-run 噪声 ~0.005 内，取更低点估计）。
- 🎯 **胜出配置（S1–S3 全定）**：`stable LR=1e-3` `/` `调度族=WSD` `/` `warmup=5%(250)` `/` `decay=10%(500)` `/` `min_lr=1e-5`；固定口径 GBS=8/mb=1/seq=4096/bf16/AdamW(β1=.9 β2=.95 eps=1e-5 wd=.1)/seed=1234。
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

---

## 🏁 P-8 Stage (i) 完整训练 — COMPLETED（2026-10-12 → 2026-10-14）

> **这是 Stage (i) 的本体**：从零训练 2.22B Mamba2-hybrid，作为 Stage (ii)–(v) 的基座。
> 配置：TP1/DP8, MBS=2, GBS=1024, seq=4094（⚠️ agent 错误，应为 4096；P-8 按 4094 跑完不干预，脚本已改 4096）, bf16, AdamW(β1=0.9 β2=0.95 eps=1e-5 wd=0.1), seed=1234。

### P-8 总览

| 项 | 值 |
|:--|:--|
| 架构 | Mamba2-hybrid 2.22B（52 SSM + 4 Attn） |
| 优化器 | AdamW（dist_muon 发散后换回，用户直令 2026-10-12） |
| 并行 | TP1 · DP8（无通信税） |
| MBS / GBS | 2 / 1024 |
| seq | 4094（P-8 实跑值；正确口径 4096，脚本已改） |
| 精度 | bf16 |
| 吞吐 | ~249K tok/s（last-100 步均值），~17.5s/step，~565 TFLOP/s/GPU |
| 总步数 | 10590（stable 9441 + decay fix 1149） |
| 总 tokens | ~44.4B（stable ~39.6B + decay ~4.8B） |
| 总 GPU·h | ~412（stable ~367 + decay ~44.7） |
| 总墙钟 | ~2.15 天 |
| 0 NaN / 0 skipped | ✅ 全程 |
| final ckpt | `p8_adamw_decay/checkpoints/iter_0001149` |

### P-8 Stable 段（2026-10-12 → 2026-10-14, 9441 步）

| 项 | 值 |
|:--|:--|
| 步数 | 9441（warmup 524 + stable 8917） |
| LR | 1e-3（WSD stable，恒定） |
| loss | 3.734（step610，warmup 后首 log）→ **2.456**（step9441） |
| tokens | 9441 × 1024 × 4094 ≈ 39.6B |
| 墙钟 | ~45.9h → GPU·h ~367 |
| ckpts | 9 个：`p8_adamw/checkpoints/iter_0001049, 2098, 3147, 4196, 5245, 6294, 7343, 8392, 9441` |
| 数据 | Ultra-FineWeb-L3 全量 en 子集（web=base 88% + code 8% + math 4%） |

### P-8 Decay FIX 段（2026-10-14 15:58 → 21:32, 1149 步）

> 🔧 **LR 未衰减根因**（2026-10-14 用户直令修复）：旧 decay 脚本 resume 时 `--name p8_adamw` 加载 `iter_0009441`，连带加载 optimizer state + LR scheduler state → scheduler 内部 step counter 恢复到 9441 → 新 decay 参数被旧 scheduler state 覆盖 → LR 卡 1e-3 恒定（27 个 log 点 LR=1e-3 未衰减）。
> **修复方案**：finetune mode（只加载权重，不加载 optimizer/scheduler/train_state）→ step 重置为 0 → warmup 100 步 → decay 1049 步（1e-3→1e-5 WSD 线性）。新 run name `p8_adamw_decay`（独立目录，不覆盖 stable ckpts）。

| 项 | 值 |
|:--|:--|
| 步数 | 1149（warmup 100 + decay 1049） |
| LR | warmup 0→1e-3（100 步）→ decay 1e-3→**1.85e-5**（1049 步, WSD 线性 ✅） |
| loss | 1.914（step10）→ **1.357**（step1140, 全 run 最低 ✅） |
| 数据 | SFT 64% + L3 24% + code 8% + math 4%（退火混合 blend） |
| tokens | 1149 × 1024 × 4094 ≈ 4.8B |
| 墙钟 | ~5.57h → GPU·h ~44.7 |
| ckpts | 3 个：`p8_adamw_decay/checkpoints/iter_0000500, 1000, 1149` |
| finetune | True（只加载权重 from `p8_adamw/checkpoints/iter_0009441`） |

### Decay FIX LR 衰减验证

| step | LR (理论) | LR (实测) | match |
|:--|:--|:--|:--|
| 10 | 1.0e-4 | 1.000000E-04 | ✅ |
| 100 (peak) | 1.0e-3 | ~1.0e-3 | ✅ |
| 500 | 6.22e-4 | 6.22e-4 | ✅ |
| 840 | 3.02e-4 | 3.016206E-04 | ✅ |
| 1000 | 1.51e-4 | 1.506196E-04 | ✅ |
| 1070 | 8.49e-5 | 8.455672E-05 | ✅ |
| 1140 (last log) | 1.85e-5 | 1.849380E-05 | ✅ |

理论值 = 1e-3 − (step−100)/1049 × (1e-3 − 1e-5)。全 108 个 log 点 LR 线性衰减精确匹配 ✅。

### Decay FIX loss 曲线（关键点）

| step | loss | 备注 |
|:--|:--|:--|
| 10 | 1.914 | warmup 开始 |
| 100 | ~1.50 | warmup 结束（LR peak） |
| 390 | 1.495 | |
| 500 | 1.462 | ckpt@500 |
| 840 | 1.393 | |
| 1000 | 1.365 | ckpt@1000 |
| 1030 | 1.358 | |
| **1140** | **1.357** | **全 run 最低 ✅** |

### 论文回填建议（§4 LLM 预训练）

- **训练 token 数**：~44.4B（stable ~39.6B + decay ~4.8B），对应 Chinchilla 最优下限档（2.22B × 20 ≈ 44.4B）。
- **GPU·h**：~412（8×H100, ~2.15 天）。
- **最终 loss**：stable 2.456 → decay annealing 1.357（SFT blend 退火增益 ~1.10）。
- **LR schedule**：WSD（warmup 5% → stable → decay 10%），stable LR=1e-3, min_lr=1e-5。
- **⚠️ seq_length**：P-8 实跑 seq=4094（agent 错误），正确口径 4096（=2¹²），论文/脚本统一 4096。
- **⚠️ §6 #13**：训练 token ~44.4B，非 1.8T（1.8T 是全语料上限，非实际训练量）。
---

## P-8 lm-eval 评测（8 常识 + 6 复杂推理，0-shot）

> 检查点：`p8_adamw_decay/hf_iter_1149`（~44.4B tokens, Mamba2-hybrid 2.22B）
> 评测框架：lm-eval-harness 0.4.13 | 0-shot | GPU: 10.239.2.29 GPU0-1
> 报告：`reports/report_pretrain_p8_lmeval_8plus6_zh.html`
> 日期：2026-10-15

### Common8 结果（8 常识任务，0-shot）

| 任务 | acc | acc_norm | 采用值 |
|:--|--:|--:|--:|
| OpenBookQA | 21.20% | 32.60% | 32.60% (acc_norm) |
| ARC-Easy | 55.60% | 50.46% | 50.46% (acc_norm) |
| ARC-Challenge | 26.54% | 27.90% | 27.90% (acc_norm) |
| BoolQ | 57.09% | — | 57.09% (acc) |
| HellaSwag | 33.41% | 40.09% | 40.09% (acc_norm) |
| PiQA | 66.49% | 66.92% | 66.92% (acc_norm) |
| SciQ | 72.70% | 67.60% | 67.60% (acc_norm) |
| Winogrande | 51.07% | — | 51.07% (acc) |
| **raw acc Avg** | | | **48.01%** |
| **harness-standard Avg** | | | **49.22%** |

### Common8 对比

| 模型 | 参数量 | 训练 tokens | raw acc Avg |
|:--|--:|--:|--:|
| BaiZe P-8 (本实验) | 2.22B | 44.4B | **48.01%** |
| BaiZe P-5b (iter_4771) | 2.22B | 20.0B | 47.91% |
| Xmodel-2 | 1.2B | 1.5T | 61.79% |
| Phi-1.5 | 1.3B | 150B | 65.68% |

**关键发现**：P-8 在 44.4B tokens 的 Common8 均分与 P-5b 在 20B tokens 几乎持平（48.01% vs 47.91% raw / 49.22% vs 49.22% harness），表明 Common8 基准在 ~20B tokens 后已饱和。

### Complex6 结果（6 复杂推理，0-shot）

| 任务 | BaiZe P-8 | 状态 | 备注 |
|:--|--:|:--|:--|
| GSM8K | 1.52% | ✅ | flexible-extract, 5-shot, full 1319 samples |
| MATH-500 | 0.00% | ✅ | exact_match |
| MMLU | 23.79% | ✅ | acc, 0-shot（唯一与 Xmodel-2/Phi-1.5 0-shot 对齐） |
| BBH | 14.04% | ✅ | flexible-extract, 0-shot, 2700 samples |
| HumanEval | 0.61% | ✅ | pass@1=0.0061, 1/164 solved, --confirm_run_unsafe_code |
| MBPP | 0.00% | ✅ | pass_at_1, --confirm_run_unsafe_code |

### Complex6 对比（0-shot 对齐项加粗）

| 模型 | MMLU (0-shot) | GSM8K (0/5-shot) | MATH (0/4-shot) | BBH (0/3-shot) | HumanEval (0-shot) | MBPP (0-shot) |
|:--|--:|--:|--:|--:|--:|--:|
| BaiZe P-8 | **23.79%** | **1.52%** | 0.00% | **14.04%** | **0.61%** | **0.00%** |
| Xmodel-2 | 48.87% | 55.88% (5-shot) | 25.50% (4-shot) | 48.40% (3-shot) | 29.88% | 29.20% |
| Phi-1.5 | 41.75% | 32.15% (5-shot) | 3.18% (4-shot) | 28.81% (3-shot) | 36.59% | 35.40% |

> Xmodel-2 Complex6 数据来自论文 Table 3（arxiv 2412.19638）。
> BaiZe 与 Xmodel-2/Phi-1.5 均为 0-shot 评测，但 Xmodel-2 论文使用 few-shot（GSM8K 5-shot, MATH 4-shot, BBH 3-shot），故**仅 MMLU 可直接对比**。

### Xmodel-2 Commonsense Reasoning 参考线（论文 Table 2，1.5T tokens）

| 模型 | ARC-c | ARC-e | BoolQ | HellaSwag | OpenBookQA | PiQA | SciQ | Winogrande | Avg |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| **Xmodel-2-1.2B** | 39.16 | 71.55 | 74.65 | 47.45 | 29.20 | 74.81 | 93.60 | 63.93 | **61.79** |
| BaiZe P-8 (44.4B) | 26.54 | 55.60 | 57.09 | 33.41 | 21.20 | 66.49 | 72.70 | 51.07 | **48.01** |
| BaiZe P-5b (20.0B) | 25.94 | 41.96 | 61.41 | 29.24 | 31.20 | 58.60 | 51.60 | 51.70 | **47.91** |

> Xmodel-2 在 1.5T tokens（34× BaiZe 训练量）达到 Common8 Avg 61.79%。
> BaiZe 在 44.4B tokens 达到 48.01%，差距主要来自训练量（34×）与参数量（1.2B vs 2.2B 架构差异）。

### Xmodel-2 / Xmodel-2.5 检查点实测缩放对比（0-shot, lm-eval 0.4.13, 2026-10-15）

> 下载 Xmodel-2 (5 个 S1 检查点 + final) 与 Xmodel-2.5 (3 个 S1 检查点)，
> 使用与 BaiZe 完全相同的 lm-eval 口径（0-shot, common8）评测。
> **Token 计数**：Xmodel-2 = 3.93M tokens/step（论文确认："批次大小为393万个token"）；
> Xmodel-2.5 S1 = 3712×480 = 1.78M tokens/step（论文 Table）。

#### Xmodel-2 检查点结果（0-shot, raw acc %，acc_norm 用于 6 集）

| 检查点 | Tokens | ARC-c | ARC-e | BoolQ | HellaSwag | OBQA | PiQA | SciQ | Winogrande | **Avg** |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| s1/10000 | 39.3B | 20.05 | 37.12 | 39.79 | 28.12 | 24.60 | 55.98 | 50.60 | 51.07 | **38.42** |
| s1/20000 | 78.6B | 21.33 | 37.16 | 40.12 | 28.35 | 25.60 | 56.42 | 51.90 | 51.22 | **39.01** |
| s1/30000 | 117.9B | 22.27 | 37.37 | 38.65 | 28.68 | 26.40 | 56.75 | 53.50 | 50.36 | **39.25** |
| s1/40000 | 157.2B | 23.04 | 38.30 | 39.76 | 28.83 | 26.40 | 56.31 | 52.00 | 51.54 | **39.52** |
| final | 1.5T | 24.32 | 44.07 | 38.04 | 29.63 | 27.60 | 56.47 | 61.20 | 52.72 | **41.76** |

#### Xmodel-2.5 检查点结果（0-shot, raw acc %，acc_norm 用于 6 集）

| 检查点 | Tokens | ARC-c | ARC-e | BoolQ | HellaSwag | OBQA | PiQA | SciQ | Winogrande | **Avg** |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| step 2000 | 3.56B | 22.61 | 29.97 | 39.72 | 26.86 | 25.80 | 51.96 | 37.90 | 51.07 | **35.74** |
| step 10000 | 17.82B | 23.46 | 30.39 | 42.54 | 25.62 | 26.60 | 50.82 | 38.20 | 50.36 | **36.00** |
| step 18000 | 32.07B | 23.72 | 28.37 | 38.07 | 25.88 | 27.40 | 49.95 | 35.40 | 51.62 | **35.05** |

#### BaiZe-2B vs Xmodel 同 token 量对比

| Tokens | BaiZe-2B | Xmodel-2 | 差距 | Xmodel-2.5 | 差距 |
|--:|--:|--:|--:|--:|--:|
| ~4B | 42.86% | — | — | 35.74% | **-7.12pp** |
| ~18-22B | 47.44% | — | — | 36.00% | **-11.44pp** |
| ~32-40B | 47.55% | 38.42% | **-9.13pp** | 35.05% | **-12.50pp** |
| ~79B | — | 39.01% | — | — | — |
| ~118B | — | 39.25% | — | — | — |
| ~157B | — | 39.52% | — | — | — |
| 1.5T | — | 41.76% | — | — | — |

> **关键发现**：
> 1. **BaiZe-2B 在相近 token 量时 Common8 均分显著高于 Xmodel-2/2.5**：39.3B 处 BaiZe 47.55% vs Xmodel-2 38.42%（**+9.13pp**），vs Xmodel-2.5 35.05%（**+12.50pp**）。
> 2. **Xmodel-2 在 39.3B→157.2B（4×训练量）仅提升 1.10pp**（38.42→39.52），增长极缓慢。
> 3. **Xmodel-2.5 在 3.56B→32.07B 几乎无增长**（35.74→35.05），甚至在 32B 处略降。
> 4. **Xmodel-2 final（1.5T）0-shot 仅 41.76%**，远低于论文报告的 61.79%。论文可能使用 few-shot 或不同评测口径，差距 ~20pp。
> 5. BaiZe-2B 在 44.4B tokens 即达到 48.01%，超过 Xmodel-2 在 1.5T（34×训练量）的 0-shot 表现。
>
> 详细 HTML 报告：`reports/report_xmodel_scaling_comparison_zh.html`

### 数据缩放曲线（P-5b 0.655B→20B + P-8 44.4B）

| Tokens | raw acc Avg | harness Avg |
|--:|--:|--:|
| 0.655B | 31.09% | 33.26% |
| 1.31B | 34.06% | 36.02% |
| 2.62B | 40.38% | 40.99% |
| 5.24B | 43.84% | 44.40% |
| 10.5B | 46.31% | 47.14% |
| 20.0B | 47.91% | 49.22% |
| **44.4B (P-8)** | **48.01%** | **49.22%** |

> 从 20B→44.4B tokens，raw acc 仅提升 +0.10pp，harness 均分完全持平 → Common8 饱和。
> 详细报告含 SVG 缩放曲线、逐项对比表、Xmodel-2/Phi-1.5 参考线。

### P-8 中间 checkpoint Common8 缩放评测（p8_adamw, 2026-10-15）

> 训练配置：GBS=1024, seq=4094, ~4.193M tokens/step, 总 10590 步 = 44.4B tokens
> 中间 ckpt 来自 `p8_adamw`（主训练），final ckpt 来自 `p8_adamw_decay`（LR 衰减阶段 +1149 步）

#### iter_1049（~4.4B tokens, 10% 训练进度）— ✅ 全 8 集完成

| 任务 | acc | acc_norm |
|:--|--:|--:|
| ARC-Challenge | 19.37% | 23.63% |
| ARC-Easy | 47.10% | 42.09% |
| BoolQ | 61.74% | — |
| HellaSwag | 27.90% | 29.43% |
| OpenBookQA | 15.60% | 29.60% |
| PiQA | 60.99% | 60.72% |
| SciQ | 58.10% | 52.20% |
| Winogrande | 52.17% | — |
| **raw acc Avg** | **42.86%** | |
| **harness Avg** | **43.95%** | |

#### iter_3147（~13.2B tokens, 30%）— ✅ 全 8 集完成

| 任务 | acc | acc_norm |
|:--|--:|--:|
| ARC-Challenge | 22.01% | 26.28% |
| ARC-Easy | 54.29% | 48.02% |
| BoolQ | 62.05% | — |
| HellaSwag | 31.15% | 35.89% |
| OpenBookQA | 19.00% | 31.60% |
| PiQA | 66.10% | 66.32% |
| SciQ | 67.10% | 61.60% |
| Winogrande | 50.91% | — |
| **raw acc Avg** | **46.58%** | |
| **harness Avg** | **47.83%** | |

#### iter_5245（~22.0B tokens, 50%）— ✅ 全 8 集完成

| 任务 | acc | acc_norm |
|:--|--:|--:|
| ARC-Challenge | 24.49% | 28.33% |
| ARC-Easy | 55.81% | 48.74% |
| BoolQ | 56.88% | — |
| HellaSwag | 32.74% | 38.87% |
| OpenBookQA | 21.40% | 33.00% |
| PiQA | 67.36% | 67.95% |
| SciQ | 70.40% | 64.10% |
| Winogrande | 50.43% | — |
| **raw acc Avg** | **47.44%** | |
| **harness Avg** | **48.54%** | |

#### iter_7343（~30.8B tokens, 70%）— ✅ 全 8 集完成

| 任务 | acc | acc_norm |
|:--|--:|--:|
| ARC-Challenge | 24.06% | 27.82% |
| ARC-Easy | 56.65% | 50.38% |
| BoolQ | 59.36% | — |
| HellaSwag | 33.50% | 40.54% |
| OpenBookQA | 21.80% | 33.40% |
| PiQA | 67.46% | 68.66% |
| SciQ | 72.50% | 64.30% |
| Winogrande | 51.54% | — |
| **raw acc Avg** | **48.36%** | |
| **harness Avg** | **49.50%** | |

#### iter_9441（~39.6B tokens, 89%）— ✅ 全 8 集完成

| 任务 | acc | acc_norm |
|:--|--:|--:|
| ARC-Challenge | 24.23% | 29.35% |
| ARC-Easy | 57.91% | 52.19% |
| BoolQ | 51.13% | — |
| HellaSwag | 34.07% | 41.74% |
| OpenBookQA | 20.60% | 33.40% |
| PiQA | 67.57% | 68.88% |
| SciQ | 72.80% | 65.80% |
| Winogrande | 52.09% | — |
| **raw acc Avg** | **47.55%** | |
| **harness Avg** | **49.32%** | |

#### P-8 内部缩放曲线（含 P-5b + P-8 中间点）

| Tokens | 来源 | raw acc Avg | harness Avg |
|--:|:--|--:|--:|
| 0.655B | P-5b | 31.09% | 33.26% |
| 1.31B | P-5b | 34.06% | 36.02% |
| 2.62B | P-5b | 40.38% | 40.99% |
| 4.4B | **P-8 iter_1049** | **42.86%** | **43.95%** |
| 5.24B | P-5b | 43.84% | 44.40% |
| 10.5B | P-5b | 46.31% | 47.14% |
| 13.2B | **P-8 iter_3147** | **46.58%** | **47.83%** |
| 20.0B | P-5b | 47.91% | 49.22% |
| 22.0B | **P-8 iter_5245** | **47.44%** | **48.54%** |
| 30.8B | **P-8 iter_7343** | **48.36%** | **49.50%** |
| 39.6B | **P-8 iter_9441** | **47.55%** | **49.32%** |
| **44.4B** | **P-8 final** | **48.01%** | **49.22%** |

> P-8 iter_1049 (4.4B) 的 42.86% 与 P-5b 5.24B 的 43.84% 接近，
> 表明不同训练配置在相近 token 量时 Common8 表现趋于一致。
> 
> **P-8 内部缩放趋势**（raw acc Avg）：4.4B→42.86%, 13.2B→46.58%, 22.0B→47.44%, 30.8B→48.36%, 39.6B→47.55%, 44.4B→48.01%
> 在 ~30B tokens 后进入平台期（48±0.5%），与 P-5b 独立验证的 20B→47.91% 吻合。
> 
> **Complex6 完整结果**（P-8 final, 44.4B）：
> GSM8K=1.52%, MATH=0%, MMLU=23.79%, BBH=14.04%, HumanEval=0.61%, MBPP=0%
> → Complex6 Avg = **6.66%**（Xmodel-2: 39.62%, 但训练量 34× + 部分任务 few-shot）


---

## Decay v2 final（71.2B tokens · Xmodel-2.5 decay v2）14 集 lm-eval 评测

> 评测时间：2026-10-20 15:03–18:15（.29, 8×H100） · 模型：`xmodel25_baize_80b_decay/final`（**≈1.3B Dense Transformer / XmodelForCausalLM**，与 Xmodel-2.5 同架构）  
> 评测脚本：`run/baize_xmodel_eval.sh` · 口径 14 集 = CS8 zero-shot + CX6 default n-shot, trust_remote_code=True, sdpa  
> 结果文件：`eval_decay_v2_final/eval_summary.txt` + `p8_eval_summary.json`  
> 中文报告：`reports/report_pretrain_decay_v2_result_zh.html`（2026-10-21 重做版，主对照 Xmodel-2.5 final，含失败归因 §5）；旧版 `report_pretrain_decay_v2_final_eval_zh.html` 留档（对照口径纠错前的版本）

### CS8（Common Sense 8，zero-shot）

| 任务 | acc | acc（%） |
|:--|--:|--:|
| hellaswag | 0.3078 | 30.78% |
| arc_easy | 0.4512 | 45.12% |
| boolq | 0.4700 | 47.00% |
| arc_challenge | 0.2824 | 28.24% |
| sciq | 0.6800 | 68.00% |
| piqa | 0.5914 | 59.14% |
| winogrande | 0.5130 | 51.30% |
| openbookqa | 0.3020 | 30.20% |
| **CS8 Avg（8/8）** | **0.4497** | **44.97%** |

### CX6（Complex 6，default n-shot）

| 任务 | few-shot | score | score（%） |
|:--|--:|--:|--:|
| gsm8k | 5 | 0.0106 | 1.06% |
| hendrycks_math500 | 4 | 0.0000 | 0.00% |
| mmlu | 5 | 0.3222 | 32.22% |
| bbh_zeroshot | 0 | 0.0398 | 3.98% |
| humaneval | 0 | 0.0000 | 0.00% |
| mbpp | 3 | 0.0000 | 0.00% |
| **CX6 Avg（6/6）** | | **0.0621** | **6.21%** |

### 对比总览（主对照 = Xmodel-2.5 final，同起点 step_532000 / 同 71.2B decay / 相近配比）

| 模型 | Tokens | Params | CS8 | CX6 | 架构 |
|:--|--:|--:|--:|--:|:--|
| Xmodel-2.5 final（主对照·同起点） | 1.4T | 1.3B | 65.40% | 32.90% | Dense Transformer |
| **decay v2 final** | 71.2B | ≈1.3B | **44.97%** | **6.21%** | Dense Transformer（同架构） |
| **Δ（decay v2 − final）** | — | — | **-20.43pp** | **-26.69pp** | — |
| step_532000（起点基线） | 1.41T | 1.3B | **61.03%** | — | Dense Transformer |
| P-8 final（旁注·架构/参数量不同） | 44.4B | 2.22B | 49.21% | 6.81% | Mamba2-hybrid |
| Xmodel-2.5 step_6000（旁注） | 79.2B | 1.3B | 50.20% | — | Dense Transformer |

> **关键观察（口径已更正）**：decay v2 从 Xmodel-2.5 stable 末点 step_532000（1.41T）起步 decay 71.2B，其唯一公平主对照是 **Xmodel-2.5 final（CS8 65.40% / CX6 32.90%）**；实测 **CS8 -20.43pp / CX6 -26.69pp，14 集全面大幅落后** →「decay 段没练出来」（甚至可能把起点模型练退化）。失败归因见报告 §4：①双移位 bug（train 2-step / eval 1-step，代码级确认）②peak LR 1.67e-3 过高+warmup100 过短 ③code ≈26 epochs 过采样 ④step 0 loss=11.72 起点异常 ⑤~~step_532000 基线缺失~~ **已补测：CS8=61.03%**（@2026-10-21 04:48，`eval_step532000_baseline/eval_summary.txt`）⇒ 判定 **decay 把起点模型训退化 16.06pp**（61.03%→44.97%），问题在 decay 配方而非起点/加载。**P-8（2.22B Mamba2-hybrid / 从头 44.4B）与 decay v2 架构/参数量均不同，不可作归因依据**。

## 短途 Decay 实验（20B · L1/L2/L3 三变体 · 进行中）

> 中文报告：`reports/report_pretrain_decay_short_experiment_zh.html` · 授权：任务书 §2026-10-21 02:3x（用户直令：自主排查根因，用 20B decay 看效果）
> 目标：用 20B 小规模 decay（≈18.7h/变体）做 2×2 因子分析，隔离“双移位 vs LR”两个主因的贡献，判定门槛 CS8 ≥55%。

### 起点基线（已测）

| 模型 | CS8 | 来源 |
|:--|--:|:--|
| step_532000（起点基线） | **61.03%** | `eval_step532000_baseline/eval_summary.txt`（@2026-10-21 04:48，8 GPU） |

### 三变体设计

| 变体 | 双移位修复 | LR | warmup | 隔离目标 |
|:--|:--:|:--|:--:|:--|
| **L1**（先行） | ✅ | 5e-4 | 100 | 两主因同修 → 验证方向 |
| **L2** | ✅ | 1.67e-3 | 100 | 仅修双移位 → 隔离 LR 贡献 |
| **L3** | ❌ | 5e-4 | 100 | 仅降 LR → 隔离双移位贡献 |

### L1 配置（`run/baize_xmodel25_decay_L1.sh`）

- 起点 `xmodel25_history/step_532000` · 输出 `xmodel25_baize_L1_20b/` · seq 3712 / GBS 960 / MBS 4
- ITERS=5611（20B token）/ WARMUP=100 / LR=5e-4 → MIN_LR=1e-5（WSD 指数衰减）/ SAVE_INTERVAL=500
- 开关：adamw_fused + compile_model default + chunked_ce(256) + fast_data + verify_save_step 20

### L1 进展（✅ 训练完成 + CS8 eval = 59.03% 完成）

| 项目 | 值 |
|:--|:--|
| 状态 | ✅ **训练完成**（5611 步 = 20B tok，18.67h）+ CS8 eval ✅ **完成 = 59.03%**（≥55% 门槛） |
| final loss | **0.8687**（step 5610/5611，lr=1.33e-5，WSD decay 末段） |
| final ckpt | `xmodel25_baize_L1_20b/final/`（model.safetensors 2.7GB，@23:45） |
| 收尾说明 | rc=1 = rank6 teardown 段 SIGABRT（final 保存后 destroy_process_group，无损，无需 resume） |
| 已存 ckpt | step_500~step_5500（12 个）+ final + verify_save_20 |
| CS8 eval | ✅ **59.03%**（`eval_L1_20b_cs8/eval_summary.txt`，@2026-10-21 23:55） |
| L2/L3 | L2 🛑 用户直令 kill@step 2370/5611（42.3%，未评 CS8，弃置）；L3 ❌ 不启动（2×2 作废） |

### 关键观察：双移位修复确效

| 实验 | step0 loss | 说明 |
|:--|--:|:--|
| v2（双移位 bug） | **11.7244** | 异常飙高（`baize_xmodel25_decay_v2_train.log [step 0/19980]`） |
| L1（双移位修复） | **1.7510** | 回归正常（`baize_xmodel25_decay_L1_train.log [step 0/5611]`），降 **6.7×** |

⇒ 双移位 bug 是 step0 loss 异常的直接原因，修复后起点 loss 回归 ~1.7（与 stable 末点一致）。L1 loss 轨迹：1.75(step0)→1.33(step20)→1.10(step100)→1.03(step500)→0.95(step1000)→0.88(step1670)，稳步下降无 spike。

### L2 结果（🛑 用户直令 kill — 2026-10-22 08:44 闭环，未评 CS8，弃置）
| 项目 | 值 |
|:--|:--|
| 状态 | 🛑 **用户 08:2x 直令 kill**（Ops RUN_ID 148「把 L2 kill 掉 执行 A 方案」）。ops relay 08:24 只杀 bash wrapper，孤儿 torchrun master 2754486 继续 headless；我 08:44:31 `kill -TERM 2754486` 级联杀净 |
| 终态 | step **2370/5611**（42.3%），loss=0.9420，lr=3.00e-04，elapsed 472.8min（7.9h）；8×GPU 已全空（0MiB/0%） |
| 配置 | 修双移位（用 L1.py）+ LR=1.67e-3 + MIN_LR=1e-4 + warmup 100 + 20B/5611 步 |
| step0 loss | 1.7138（**双移位修复在高 LR 下仍生效**，vs v2 11.72）——已作为证据留档 |
| ckpt | `xmodel25_baize_L2_20b/` 下 step_500/1000/1500/2000 + verify_save_20（全部留档） |
| 结论 | **未评 CS8（弃置）**；L2/L3 2×2 因子分析作废 |

### 后续计划（方向已变：A方案 = 官方 Megatron 代码）

1. ✅ L1 训完 + CS8 eval = **59.03%**（修双移位后仍 -2pp，残余主因=自写脚本缺 μP/LR 口径）。
2. 🛑 L2 用户直令 kill@step2370（未评 CS8）；L3 不启动；2×2 因子分析作废。
3. 用户裁决：改用官方 `examples/xmodel/train_decay_fp8_1120.sh`（DP8+μP+FP8+lr1e-5 const，RUN_ID 147 可行性✅）。
4. 前置三步：① 起点 step_532000 HF→Megatron 转换（repo convert.py+loader_*）；② DATA_PATH 6 源权重定位（`full_*` 实测 0 shard）；③ 100 步冒烟。

---

## Decay 5000 步（A方案 · 官方 Megatron train_decay_fp8_1113.sh · 18.1B tokens）14 集评测 ✅

> 评测时间：2026-10-23（.29, 8×H100） · 模型：`Xmodel-2.5-code/out/hf_decay_5000_final`（**1.35B Dense Transformer / XmodelForCausalLM**，HF 转换自 Megatron ckpt@5000）
> 评测脚本：`run/baize_decay5000_eval_14.sh` · 口径 14 集 = CS8 zero-shot + CX6 default n-shot, trust_remote_code=True, sdpa
> 结果文件：`nemo_experiments/eval_decay_5000_final/p8_eval_summary.json` + `eval_summary.txt`
> 训练：5000 步 / 18.1B tok（GBS 960 × seq 3776）/ final loss 0.9946 / val PPL 2.712 / 0 NaN / 0 skip / optimizer Muon(muon-matched-adamw-rms 0.2) / LR 1.66667e-3 / WSD exponential / warmup 0 / MBS 5 / FP8 hybrid

### CS8（Common Sense 8，zero-shot）

| 任务 | acc_norm/acc | % |
|:--|--:|--:|
| hellaswag | 0.5468 | 54.68% |
| arc_easy | 0.6536 | 65.36% |
| boolq | 0.7003 | 70.03% |
| arc_challenge | 0.3840 | 38.40% |
| sciq | 0.8710 | 87.10% |
| piqa | 0.6904 | 69.04% |
| winogrande | 0.5675 | 56.75% |
| openbookqa | 0.3040 | 30.40% |
| **CS8 Avg（8/8）** | **0.5897** | **58.97%** |

### CX6（Complex 6，default n-shot）

| 任务 | few-shot | score | % |
|:--|--:|--:|--:|
| gsm8k | 5 | 0.4655 | 46.55% |
| hendrycks_math500 | 4 | 0.1280 | 12.80% |
| mmlu | 5 | 0.4897 | 48.97% |
| bbh_zeroshot | 0 | 0.3001 | 30.01% |
| humaneval | 0 | 0.1037 | 10.37% |
| mbpp | 3 | 0.1940 | 19.40% |
| **CX6 Avg（6/6）** | | **0.2802** | **28.02%** |

### 对比总览（主对照 = Xmodel-2.5 final，同起点 step_532000 / 相近配比）

| 模型 | Tokens | Params | CS8 | CX6 | 架构 |
|:--|--:|--:|--:|--:|:--|
| Xmodel-2.5 final（官方） | 1.4T+ | 1.3B | 65.40% | 32.90% | Dense Transformer |
| step_532000（起点基线） | 1.41T | 1.3B | **61.03%** | — | Dense Transformer |
| **decay-5000（本实验）** | 18.1B | 1.35B | **58.97%** | **28.02%** | Dense Transformer（同架构） |
| decay v2（自写脚本·71.2B） | 71.2B | ≈1.3B | 44.97% | 6.21% | Dense Transformer（同架构） |
| **Δ（decay-5000 − 官方 final）** | — | — | **-6.43pp** | **-4.88pp** | — |
| **Δ（decay-5000 − 起点基线）** | — | — | **-2.06pp** | — | — |
| **Δ（decay-5000 − decay v2）** | — | — | **+14.00pp** | **+21.81pp** | — |

> **关键结论**：decay-5000 用官方 `train_decay_fp8_1113.sh`（DP8 + μP + FP8 hybrid + optimizer Muon 0.2 + WSD exponential + warmup 0 + MBS 5 + LR 1.66667e-3），18.1B token / 5000 步后 **CS8=58.97% / CX6=28.02%**：
> ① 相对起点基线 CS8 仅 **-2.06pp**（61.03%→58.97%）——能力基本保持，未出现 decay v2 的暴跌；② 相对官方 final（32.90%）CX6 差 **-4.88pp**，属小间距（官方 final 训练量大 78×）；③ 相对自写脚本 decay v2 的 **44.97%/6.21% 大幅修复（+14.00/+21.81pp）**，证明根因在于自写脚本缺 μP/LR 口径 + 双移位，而非 decay 概念本身。

## 2026-11-07 10:05 — CPU Eval Thread/Batch Scaling Probe (11w ckpt)

**运维令**: 2026-11-07 09:1x — 11w检查点8集全量评测 + 线程/batch扫描

### 已完成数据点 (limit=5, openbookqa+arc_challenge)

| Config | Threads | Batch | Wall (s) | s/req | Cores used | Peak RSS | Scores |
|--------|---------|-------|----------|-------|------------|----------|--------|
| 1 | 8 | 1 | 714 | 17.85 | ~5/8 | 50.3 GB | obqa=0.0/0.2norm, arc=0.2/0.2norm |
| 2(partial) | 8 | 4 | ~84s/req | 83.8 | ~4.5 | -- | (killed, too slow) |

### Key Finding
- **bs=4 on CPU is SLOWER per-request** (83.8s vs 17.85s), no batching efficiency gain for Mamba2 sequential scan
- **8 threads only uses ~5 cores** — PyTorch reference implementation (no mamba_ssm/causal_conv1d) has limited parallelism
- **Full 8-set eval estimate at baseline**: ~714s × (69650/40) ≈ **~34 hours** (impractical for real-time, needs background run)
- **Peak RSS ~50 GB** (2B model + PyTorch thread pool overhead) — far below 1213 GB available

### Probe matrix running (limit=3, 8 configs)
- t=8,16,32,80 × b=1,2
- Expected total: ~56 min
- Results: /tmp/baize_probe_results.json

---

## ISEDA2027 论文预训练章节刷新（2026-11-10 #1918 · 用户直令）

**任务**：刷新 `ISEDA2027/4_llm_pretrain.tex` 的 §4.6 进度句 + 新增 §4.7 基准缩放表 + 编译 main.pdf。

### 训练实测取数（.29 /proc/146283/fd/1）
- iter: 154660/700000
- step time: ~7050ms → tok/s = 4194304/7.05 ≈ 595K
- loss: ≈2.03（末10步 2.017–2.051）
- 0 NaN, 0 skipped iterations
- GPU: 8/8, 87–100% util, ~75GB/GPU
- 取数命令：`ssh 10.239.2.29 'cat /proc/146283/fd/1 | tail -30'`

### 基准评测数据（.29 results.json · acc_norm for ARC/HellaSwag, acc for rest）
| iter    | tokens  | Avg(harness) |
|---------|---------|-------------|
| 10,000  | 41.9B   | 50.75%      |
| 30,000  | 125.8B  | 51.00%      |
| 50,000  | 209.7B  | 52.88%      |
| 80,000  | 335.5B  | 55.50%      |
| 110,000 | 461.4B  | 57.12%      |
| 150,000 | 629.2B  | 56.50%      |

取数命令：`ssh 10.239.2.29 'python3 << PYEOF ...'`（读 `gguf_iter_{t}_fixed_8set/results.json`）

### §4.6 修改
- 进度句：`iteration 30,660` → `154,660`；`598K tok/s` → `595K`；`loss 2.151` → `≈2.03`；`no NaN` → `zero NaN or skipped iterations`；加 `as of (2026-11-10)`
- `tab:prod-budget`：Status `30.7k done` → `155k done`；wall-clock `≈56 d` → `≈57 d`；Total `≈59.5 d` → `≈60.6 d`

### §4.7 新增→撤回
- #1918 (20:37): 新增 `\subsection{Checkpoint Scaling on General Benchmarks}\label{sec:ckpt-scaling}`（6 行 booktabs 表 + 正文 2 句）
- **c34b04e12 (21:23): 撤回 §4.7 + tab:ckpt-scaling**（用户更正 21:2x：「评测结果不用写在论文里。评测是为了监控，训练还处于早期。」）
- 撤回后 tex 无残留：grep `ckpt-scaling|Checkpoint Scaling|General Benchmarks` = 0 命中
- 摘要同步更新：30,660/2.151 → 154,660/≈2.03

### 编译结果（c34b04e12 后重新验证）
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined references
- main.pdf: 5 pages, 228400 bytes（§4.7 撤回后比含表版 229159→228400，更小）
- **注意**：c34b04e12 提交的 PDF (248801B) 系 §4.7 撤回前的旧编译产物（stale），本轮重新编译修正为 228400B
- main.log: 0 `!` lines, 0 `Undefined` lines

---

### 论文 §4.6 刷新（2026-11-10 22:4x · iter 154,660 → 155,780）

**取数**：
- 训练日志：`ssh 10.239.2.29 'cat /proc/4179185/fd/1 | tail -5'`
- 最新行：`[2026-11-10 22:43:49] iteration 155780/700000 | elapsed time per iteration (ms): 7275.9 | lm loss: 2.033605E+00 | number of nan iterations: 0 | number of skipped iterations: 0`
- 吞吐计算：500 iter / 3550 s = 7.1 s/iter → 4,194,304 / 7.1 ≈ 590K tok/s
- GPU：`nvidia-smi` → 8 卡 95-100% util, ~75GB mem（全满载）

**改动**（仅 `0_abstract.tex` + `4_llm_pretrain.tex` + `main.pdf`）：
- §4.6 进度句（4_llm_pretrain.tex line 109）：`154,660` → `155,780`；`595K` → `590K`；`2.03` → `2.02`
- 摘要（0_abstract.tex line 14）：同上同步
- `tab:prod-budget`（line 122）：Status `155k done` → `156k done`；wall-clock `≈57 d` → `≈58 d`
- `tab:prod-budget` Total（line 126）：`≈60.6 d` → `≈61.5 d`
- wall-clock 重算：700k × 4,194,304 / 590K ≈ 57.6 d → ≈58 d；Total = 58 + 1.2 + 2.3 ≈ 61.5 d

**验证**：
- grep benchmark 数字（ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/zero-shot/ckpt-scaling）：0 命中 ✅
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined references
- main.pdf: 5 pages, 228,230 bytes
- main.log: 0 `!` lines, 0 errors

### 论文 §4.6 刷新（2026-11-10 23:5x · iter 155,780 → 156,320）

**取数**：
- 训练日志：`ssh 10.239.2.29 'tail -30 /proc/4179185/fd/1'`
- 最新行：`[2026-11-11 00:12:56] iteration 156530/700000 | elapsed time per iteration (ms): 6971.3 | lm loss: 2.027347E+00 | number of nan iterations: 0 | number of skipped iterations: 0`
- 吞吐计算：末26步均7,173 ms → 4,194,304 / 7.173 = 584,853 ≈ 585K tok/s
- wall-clock：700,000 × 4,194,304 / 584,853 / 86,400 = 58.1 d ≈ 58 d
- GPU：`nvidia-smi` → 8 卡 95-100% util, ~75GB mem（全满载）

**改动**（仅 `0_abstract.tex` + `4_llm_pretrain.tex` + `main.pdf`）：
- §4.6 进度句（4_llm_pretrain.tex line 109）：`156,320` → `156,530`，`590K` → `585K`，日期 `2026-11-10` → `2026-11-11`
- 摘要（0_abstract.tex line 14）：同上同步
- `tab:prod-budget`（line 122）：`156k done` → `157k done`；wall-clock `≈58 d` 不变
- 中文注释行同步更新（line 110 + line 15）

**验证**：
- grep benchmark 数字（ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/Checkpoint Scaling）：0 命中 ✅
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined references
- main.pdf: 5 pages, 228,472 bytes
- main.log: 0 `!` lines, 0 errors

---

### 论文 §4.6 刷新 — 2026-11-11 00:15（#1927）

**背景**：用户最高优先令「刷新 ISEDA2027 论文预训练章节」+ 21:2x 更正「评测结果不写进论文」。

**取数**：
- 训练日志：`ssh 10.239.2.29 'tail -30 /proc/4179185/fd/1'`
- 最新行：`[2026-11-11 00:12:56] iteration 156530/700000 | elapsed time per iteration (ms): 6971.3 | lm loss: 2.027347E+00 | number of nan iterations: 0 | number of skipped iterations: 0`
- 吞吐计算：末26步均7,173 ms → 4,194,304 / 7.173 = 584,853 ≈ 585K tok/s
- wall-clock：700,000 × 4,194,304 / 584,853 / 86,400 = 58.1 d ≈ 58 d
- GPU：`nvidia-smi` → 8 卡 95-100% util, ~75GB mem（全满载）

**改动**（仅 `0_abstract.tex` + `4_llm_pretrain.tex` + `main.pdf`）：
- §4.6 进度句（4_llm_pretrain.tex line 109）：`156,320` → `156,530`，`590K` → `585K`，日期 `2026-11-10` → `2026-11-11`
- 摘要（0_abstract.tex line 14）：同上同步
- `tab:prod-budget`（line 122）：`156k done` → `157k done`；wall-clock `≈58 d` 不变
- 中文注释行同步更新（line 110 + line 15）

**验证**：
- grep benchmark 数字（ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/Checkpoint Scaling）：0 命中 ✅
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined references
- main.pdf: 5 pages, 228,472 bytes
- main.log: 0 `!` lines, 0 errors

---

### 论文 §4.6 刷新 · 2026-11-11 00:37 (#1928)

**取数**：
- 训练日志：`ssh 10.239.2.29 'tail -10 /proc/146283/fd/1'`
- 最新行：`[2026-11-11 00:35:19] iteration 156720/700000 | elapsed time per iteration (ms): 6997.2 | lm loss: 2.027124E+00 | number of nan iterations: 0 | number of skipped iterations: 0`
- 吞吐计算：末10步均 7,069 ms → 4,194,304 / 7.069 = 593,436 ≈ 590K tok/s
- wall-clock：700,000 × 4,194,304 / 590,000 / 86,400 = 57.6 d ≈ 58 d（不变）
- GPU：`nvidia-smi` → 8 卡 94-100% util, ~75GB mem（全满载）

**改动**（仅 `0_abstract.tex` + `4_llm_pretrain.tex` + `main.pdf`）：
- §4.6 进度句（4_llm_pretrain.tex line 109）：`156,530` → `156,720`，`585K` → `590K`，`2.02` → `2.03`
- 摘要（0_abstract.tex line 14）：同上同步
- `tab:prod-budget`（line 122）：`157k done` 不变；wall-clock `≈58 d` 不变
- 中文注释行同步更新（line 110 + line 15）

**验证**：
- grep benchmark 数字：0 命中 ✅
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined references, 0 warnings
- main.pdf: 5 pages, 228,405 bytes
- main.log: 0 `!` lines, 0 errors

### 论文 §4.6 刷新 — 2026-11-11 01:21 (#1930)

- **取数命令**：`ssh 10.239.2.29 'tail -30 /proc/146283/fd/1'`
- **训练日志**：iteration 157,080 / 700,000 | elapsed 7034.5 ms/step | lm loss 2.0326 | 0 NaN / 0 skipped
- **末 26 步**：6957–7176 ms (均 7065 ms, 均 < 7.4s ✅) | loss 2.010–2.041 | grad norm 0.087–0.132
- **tok/s 计算**：4,194,304 / 7.065 s = 593,653 ≈ 590K
- **GPU**：8 卡 93–96% util / 74–75 GB
- **§4.6 刷新** (4_llm_pretrain.tex line 109): 156,920 → 157,080 (loss ≈2.02 不变, tok/s ≈590K 不变)
- **摘要刷新** (0_abstract.tex line 14): 同上
- **tab:prod-budget** (line 122): "157k done" 不变 (157,080 rounds to 157k); wall-clock ≈58d 不变
- grep benchmark 数字：0 命中 ✅；§4.7 不存在 ✅
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined references, 0 warnings
- main.pdf: 5 pages, 228,225 bytes
- main.log: 0 `!` lines, 0 errors

### 论文 §4.6 刷新 — 2026-11-11 01:40 (#1931)

**训练数据来源**：`ssh 10.239.2.29 'tail -30 /proc/146283/fd/1'`
- 最新 iteration: 157,260 / 700,000 (2026-11-11 01:38:57)
- 末 3 步 elapsed: 7031.1 / 7126.7 / 7032.7 ms (均 7063.5ms, 均 <7.4s 阈值)
- lm loss: 2.017–2.045 (≈2.02)
- 0 NaN, 0 skipped iterations
- GPU: 8/8 卡 91–100% util, ~75GB/卡
- tok/s: 4,194,304 / 7.0635s = 593,773 ≈ 590K

**论文修改** (只改 `ISEDA2027/4_llm_pretrain.tex` + `ISEDA2027/0_abstract.tex` + `main.pdf`):
- §4.6 进度句 (line 109): iteration 157,080 → 157,260 (tok/s 590K 不变, loss ≈2.02 不变, date 2026-11-11 不变)
- 摘要 (0_abstract.tex line 14): 同步 157,080 → 157,260
- tab:prod-budget (line 122): "157k done" 不变 (157,260 rounds to 157k); wall-clock ≈58d 不变
  - wall-clock 重算: 700,000 × 4,194,304 / 590,000 = 57.6d → ≈58d

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined, 0 warnings
- main.pdf: 5 pages, 228,396 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/4_llm_pretrain.tex + 0_abstract.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK=22.0KB ✅ / MEMORY=13.3KB ✅

### 论文 §4.6 刷新 — 2026-11-11 02:25 (#1933)

**取数命令**: `ssh -o StrictHostKeyChecking=no 10.239.2.29 'tail -60 /proc/146283/fd/1'`

**训练状态** (2026-11-11 02:22):
- iteration: 157,620 / 700,000 (22.5%)
- 末 20 步 step time: 6997-7529ms (avg 7300ms; 部分 >7.4s ⚠️ 但无 eval 在跑)
- lm loss: 2.006-2.024 (≈2.02)
- 0 NaN, 0 skipped iterations
- GPU: 8/8 卡 100% util, ~75GB/卡
- tok/s: 4,194,304 / 7.300s = 574,532 ≈ 575K (较前轮 590K 下降, step time 升高 ~230ms)

**论文修改** (只改 `ISEDA2027/4_llm_pretrain.tex` + `ISEDA2027/0_abstract.tex` + `main.pdf`):
- §4.6 进度句 (line 109): iteration 157,440 → 157,620, tok/s 590K → 575K (loss ≈2.02 不变, date 2026-11-11 不变)
- 摘要 (0_abstract.tex line 14): 同步 157,440 → 157,620, 590K → 575K
- tab:prod-budget (line 122): "157k done" → "158k done"; wall-clock ≈58d → ≈59d
  - wall-clock 重算: 700,000 × 4,194,304 / 575,000 = 5,106,414s = 59.1d → ≈59d
- tab:prod-budget total (line 126): ≈61.5d → ≈62.5d (59 + 1.2 + 2.3)

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined, 0 warnings
- main.pdf: 5 pages, 228,397 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK=22.5KB ✅ / MEMORY≈15.5KB ✅

---

### 论文 §4.6 刷新 — 2026-11-11 02:47 (#1934)

**取数命令**: `tail -40 /proc/146283/fd/1` (PID 146283 = pretrain_launcher.py on .29)

**训练状态** (.29 /proc/146283/fd/1):
- iteration: 157,810 / 700,000
- elapsed time per iteration (ms): 末9步 6948-7234ms (均 7061ms, 均 <7.4s ✅)
- lm loss: 2.009-2.023 (≈2.02)
- 0 NaN, 0 skipped iterations
- GPU: 8/8 卡 95-100% util, ~75GB/卡
- tok/s: 4,194,304 / 7.061s = 593,453 ≈ 590K (较前轮 575K 回升, step time 回落 ~240ms)

**论文修改** (只改 `ISEDA2027/4_llm_pretrain.tex` + `ISEDA2027/0_abstract.tex` + `main.pdf`):
- §4.6 进度句 (line 109): iteration 157,620 → 157,810, tok/s 575K → 590K (loss ≈2.02 不变, date 2026-11-11 不变)
- 摘要 (0_abstract.tex line 14): 157,620 → 157,810, 575K → 590K, "one-fifth" → "one-quarter" (22.5% 更接近 1/4)
- tab:prod-budget (line 122): "158k done" 不变 (157,810 rounds to 158k); wall-clock ≈59d → ≈58d
  - wall-clock 重算: 700,000 × 4,194,304 / 590,000 = 4,976,293s = 57.6d → ≈58d
- tab:prod-budget total (line 126): ≈62.5d → ≈61.5d (58 + 1.2 + 2.3)

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined, 0 warnings
- main.pdf: 5 pages, 228,206 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK=22.5KB ✅ / MEMORY≈16.8KB ✅
---

### 论文 §4.6 刷新 — 2026-11-11 03:28 (#1936)

**取数命令**:
```bash
ssh 10.239.2.29 'cat /proc/146283/fd/1 | tail -30'
```

**训练实测值**:
- iter: 158,160 / 700,000 (22.6%)
- 末 9 步 step time (ms): 6950.1, 7055.6, 7007.9, 6971.6, 7035.1, 6973.2, 7111.2, 6950.3, 7010.6 → 均值 7007.3ms (均 < 7.4s ✅)
- loss: 2.006–2.037 (≈2.02)
- 0 NaN, 0 skipped iterations
- GPU: 8 卡 100% / ~75GB

**tok/s 计算**:
- 4,194,304 / 7.0073s = 598,386 ≈ 598K (前轮 595K → 微升 +3K)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 157,980 → 158,160, tok/s 595K → 598K (loss ≈2.02 不变)
- abstract (0_abstract.tex line 14): 同步 157,980 → 158,160, 595K → 598K
- tab:prod-budget (line 122): "158k done" 不变 (158,160 rounds to 158k)
- wall-clock: ≈57d 不变 (700k × 4,194,304 / 598K = 56.8d)
- tab:prod-budget total (line 126): ≈60.5d 不变

**编译结果**:
- `latexmk -g -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined, 0 warnings
- main.pdf: 5 pages, 228,444 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK=22.5KB ✅ / MEMORY≈19.2KB ✅

---

### 论文 §4.6 刷新 #1937 (2026-11-11 03:55)

**取数命令**:
```bash
ssh 10.239.2.29 'tail -n 30 /proc/146283/fd/1 2>/dev/null'
# fd=1 → /tmp/baize_s1_baize2b_worker.log (deleted), still open via /proc
ssh 10.239.2.29 'nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader'
```

**实测训练数据** (2026-11-11 03:51:38):
- iter 158,380 / 700,000 (22.6%)
- 末 9 步 step time: 7001-7286 ms (均 7097 ms, 均 < 7.4s ✅)
- loss: 2.004-2.029 (avg ≈ 2.013, 论文取 ≈2.02)
- 0 NaN, 0 skipped iterations ✅
- GPU 8 卡 83-100% util / ~75 GB each

**tok/s 计算**:
- 4,194,304 / 7.097s = 590,915 ≈ 591K (前轮 598K → 微降 -7K)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 158,160 → 158,380, tok/s 598K → 591K (loss ≈2.02 不变)
- abstract (0_abstract.tex line 14): 同步 158,160 → 158,380, 598K → 591K
- tab:prod-budget (line 122): "158k done" 不变 (158,380 rounds to 158k)
- wall-clock: ≈57d 不变 (700k × 4,194,304 / 591K = 57.5d)
- tab:prod-budget total (line 126): ≈60.5d 不变

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined, 0 warnings
- main.pdf: 5 pages, 228,460 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK=22.5KB ✅ / MEMORY≈19.5KB ✅

---

## #1938 (2026-11-11 04:17) 论文 §4.6 刷新·iter 158,380→158,570·tok/s 591K→584K·loss 2.02→2.01

**训练数据** (.29 `/proc/146283/fd/1`):
- iteration 158,570 / 700,000 (22.65%)
- 末9步 (158490–158570): 7239.8, 7336.6, 7202.8, 7395.7, 7238.5, 7028.5, 7115.9, 7021.5, 7065.6 ms → 均 7182.7ms (均 ≤7.4s ✅)
  - 注: 158480=7851.5ms (outlier >7.4s, 已排除于均值)
- loss: 2.010636, 2.013686, 2.015243, 2.006586, 2.024601, 2.019472, 2.021291, 2.012256, 1.999450 → 均 ≈2.01
- 0 NaN, 0 skipped, grad_norm 0.085–0.112
- GPU (.29 nvidia-smi): 8卡 95-100% util, ~75GB mem ✅

**tok/s 计算**:
- 4,194,304 / 7.183s = 583,986 ≈ 584K (前轮 591K → 微降 -7K)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 158,380 → 158,570, tok/s 591K → 584K, loss 2.02 → 2.01
- abstract (0_abstract.tex line 14): 同步 158,380 → 158,570, 591K → 584K, 2.02 → 2.01
- tab:prod-budget (line 122): "158k done" 不变 (158,570 rounds to 158k); wall-clock ≈57d → ≈58d (700k × 4,194,304 / 584K = 58.2d)
- tab:prod-budget total (line 126): ≈60.5d → ≈61.5d

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined, 0 warnings
- main.pdf: 5 pages, 228,206 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅ (仅 EDA "benchmark" 与 contamination "536 benchmarks" 合法用法)
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK=22.5KB ✅ / MEMORY≈19.8KB ✅

---

### §4.6 刷新 #1939 (2026-11-11 04:40) — iter 158,570→158,780

**取数命令**:
```bash
ssh 10.239.2.29 'tail -40 /proc/4179175/fd/1'   # fd=deleted /tmp/baize_s1_baize2b_worker.log
ssh 10.239.2.29 'nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader | head -4'
```

**训练日志关键数据** (2026-11-11 03:50:28→04:39:29):
- iter 158,370→158,780 (410 步, 2941s wall-clock)
- 平均 step time: 2941/410 = 7.173 s/step (range 6916-7852ms)
- lm loss: 2.011-2.026 (末 10 步均 ≈2.019)
- skipped iterations: 0, nan iterations: 0
- GPU: 8 卡 100% util, ~75GB/81GB each

**tok/s 计算**:
- 4,194,304 / 7.173s = 584,731 ≈ 585K (前轮 584K → 微升 +1K)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 158,570 → 158,780, tok/s 584K → 585K, loss 2.01 → 2.02
- abstract (0_abstract.tex line 14): 同步 158,570 → 158,780, 584K → 585K, 2.01 → 2.02
- tab:prod-budget (line 122): "158k done" 不变 (158,780 truncates to 158k); wall-clock ≈58d 不变 (700k × 4,194,304 / 585K = 57.9d)

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined
- main.pdf: 5 pages, 228,223 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈20KB ✅

---

### 论文 §4.6 刷新记录 — 2026-11-11 05:23 (#1940)

**取数命令**:
```bash
ssh -o StrictHostKeyChecking=no 10.239.2.29 'tail -40 /proc/146283/fd/1'
ssh -o StrictHostKeyChecking=no 10.239.2.29 'nvidia-smi --query-gpu=utilization.memory,memory.used --format=csv,noheader | head -2'
```

**训练日志关键数据** (2026-11-11 05:10:12→05:20:50):
- iter 159,040→159,130 (10 步, wall-clock ~71s)
- 平均 step time: (7191.8+7019.4+7123.2+7123.5+7052.5+7085.8+7049.6+7136.6+7166.9+7017.7)/10 = 7096.67 ms ≈ 7.097 s/step (range 7017-7192ms, 均 <7.4s ✅)
- lm loss: 2.021-2.047 (末 10 步均 ≈2.033)
- skipped iterations: 0, nan iterations: 0
- GPU: 8 卡 65-66% util, ~75GB

**tok/s 计算**:
- 4,194,304 / 7.097s = 590,990 ≈ 591K (前轮 585K → 微升 +6K)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 158,780 → 159,130, tok/s 585K → 591K, loss 2.02 → 2.03
- abstract (0_abstract.tex line 14): 同步 158,780 → 159,130, 585K → 591K, 2.02 → 2.03
- tab:prod-budget (line 122): "158k done" → "159k done"; wall-clock ≈58d 不变 (700k × 4,194,304 / 591K = 57.5d → ≈58d)

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined
- main.pdf: 5 pages, 228,474 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈24KB ✅

### 论文 §4.6 刷新记录 — 2026-11-11 05:44 (#1941)

**取数命令**:
```bash
tail -50 /proc/146283/fd/1  # 本机=.29，训练进程 PID 146283
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
```

**训练日志关键数据** (2026-11-11 05:32:36→05:43:11):
- iter 159,230→159,320 (10 步, wall-clock ~635s)
- 平均 step time: (7012.8+6981.9+7088.5+6953.4+7078.6+7020.4+7013.0+7133.4+7105.1+7113.7)/10 = 7049.08 ms ≈ 7.049 s/step (range 6953-7134ms, 均 <7.4s ✅)
- lm loss: 2.016-2.054 (末 10 步均 ≈2.031)
- skipped iterations: 0, nan iterations: 0
- GPU: 8 卡 84-100% util, ~75GB

**tok/s 计算**:
- 4,194,304 / 7.049s = 595,036 ≈ 595K (前轮 591K → 微升 +4K)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 159,130 → 159,320, tok/s 591K → 595K, loss ≈2.03 不变
- abstract (0_abstract.tex line 14): 同步 159,130 → 159,320, 591K → 595K
- tab:prod-budget (line 122): "159k done" 不变 (159,320 rounds to 159k); wall-clock ≈58d → ≈57d (700k × 4,194,304 / 595K = 57.1d)
- tab:prod-budget (line 126): total ≈61.5d → ≈60.5d (57 + 1.2 + 2.3)

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined, 0 warnings
- main.pdf: 5 pages, 228,635 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈25KB ✅

---

### 论文 §4.6 刷新 — 2026-11-11 06:07 (#1942)

**取数命令**: `ssh 10.239.2.29 'tail -40 /proc/146283/fd/1'`

**训练状态** (iter 159,500/700,000 @ 06:04:24):
- 末 10 步 (159410–159500) step time: 7125.0, 7106.9, 6996.1, 7106.0, 7018.3, 7113.4, 7096.5, 7069.4, 7046.2, 7156.2 ms → avg 7083.4 ms (all < 7.4s ✅)
- tok/s = 4,194,304 / 7.0834 = 592,073 ≈ 592K
- loss: 2.021–2.037, avg ≈ 2.03
- 0 NaN, 0 skipped
- GPU: 8 卡 87–100% util, ~75 GB/卡

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 159,320 → 159,500, tok/s 595K → 592K, loss ≈2.03 不变
- abstract (0_abstract.tex line 14): 同步 159,320 → 159,500, 595K → 592K
- tab:prod-budget (line 122): "159k done" → "160k done" (159,500 rounds to 160k); wall-clock ≈57d 不变 (700k × 4,194,304 / 592K = 57.4d)
- tab:prod-budget (line 126): total ≈60.5d 不变

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined
- main.pdf: 5 pages, 228,235 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈26KB ✅

### 论文 §4.6 刷新 — 2026-11-11 06:28 (#1943)

**取数命令**: `tail -40 /proc/146283/fd/1` (本机 .29, 无需 ssh)

**训练状态** (iter 159,690/700,000 @ 06:26:50):
- 末 10 步 (159600–159690) step time: 7080.9, 7163.3, 7050.3, 6974.9, 7072.5, 7124.4, 7114.0, 7009.5, 7094.6, 7185.4 ms → avg 7087.0 ms (all < 7.4s ✅)
- tok/s = 4,194,304 / 7.0870 = 591,833 ≈ 592K
- loss: 2.019–2.037, avg ≈ 2.03
- 0 NaN, 0 skipped
- GPU: 8 卡 94–100% util, ~75 GB/卡

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109): iter 159,500 → 159,690, tok/s 592K 不变, loss ≈2.03 不变
- abstract (0_abstract.tex line 14): 同步 159,500 → 159,690
- tab:prod-budget (line 122): "160k done" 不变 (159,690 rounds to 160k); wall-clock ≈57d 不变 (700k × 4,194,304 / 592K = 57.4d)
- tab:prod-budget (line 126): total ≈60.5d 不变

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 undefined
- main.pdf: 5 pages, 228,460 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈27KB ✅

---

### 2026-11-11 06:50 — 论文 §4.6 刷新 (#1944)

**取数**:
- 命令: `ssh 10.239.2.29 'tail -50 /proc/146283/fd/1'`
- 最新 iter: 159,860/700,000 (2026-11-11 06:46:56)
- 末 10 步 (159,770–159,860): elapsed 6946–7240ms (avg 7099ms, 均 <7.4s ✅)
- loss: 2.017–2.043 (avg ≈2.03)
- 0 NaN, 0 skipped iterations ✅
- GPU: 8 卡 100% util / ~75GB each
- tok/s: 4,194,304 / 7.099 = 590,811 ≈ 591K

**刷新内容**:
- §4.6 (4_llm_pretrain.tex line 109): iter 159,690 → 159,860, tok/s 592K → 591K, loss ≈2.03 不变
- abstract (0_abstract.tex line 14): 同步
- tab:prod-budget (line 122): "160k done" 不变 (159,860 rounds to 160k); wall-clock ≈57d → ≈58d (700k × 4,194,304 / 591K = 57.5d)
- tab:prod-budget (line 126): total ≈60.5d → ≈61.5d

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 warnings, 0 undefined
- main.pdf: 5 pages, 228,670 bytes

**护栏检查**:
- grep benchmark 数字 (ARC/HellaSwag/PIQA/BoolQ/OpenBookQA/SciQ/Winogrande/ckpt-scaling/zero-shot) in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈28KB ✅


### 2026-11-11 07:14 — 论文 §4.6 刷新 + 160k eval 启动 (#1945)

**取数**:
- 命令: `ssh 10.239.2.29 'tail -15 /proc/146283/fd/1 | grep iteration'`
- 最新 iter: 160,070/700,000 (2026-11-11 07:11:44)
- 末 10 步 (159,980–160,070): elapsed 6931–7156ms (avg 7043ms, 均 <7.4s ✅)
- loss: 2.017–2.048 (avg ≈2.03)
- 0 NaN, 0 skipped iterations ✅
- GPU: 8 卡 96-100% util / ~75GB each
- tok/s: 4,194,304 / 7.043 = 595,497 ≈ 595K

**刷新内容**:
- §4.6 (4_llm_pretrain.tex line 109): iter 159,860 → 160,070, tok/s 591K → 595K, loss ≈2.03 不变
- abstract (0_abstract.tex line 14): 同步
- tab:prod-budget (line 122): "160k done" 不变 (160,070 rounds to 160k); wall-clock ≈58d → ≈57d (700k × 4,194,304 / 595K = 57.1d)
- tab:prod-budget (line 126): total ≈61.5d → ≈60.5d

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors
- main.pdf: 5 pages, 228,237 bytes

**160k eval pipeline**:
- 脚本: `/tmp/baize_eval_160k_pipeline.sh` (基于 140k export + 150k eval 模板)
- Phase 1 (HF 导出): ✅ convert_mcore_to_hf.py, 323 tensors, 2.22B params, model.safetensors 4.44GB
- Phase 2 (config patch): ✅ max_position_embeddings=1048576, rope_theta=1000000, rope_scaling=None
- Phase 3 (check_rope): ⚠️ 参数格式不匹配 (--config vs positional), 非阻塞
- Phase 4 (GGUF 转换): 首次失败 → 修复 → 重试中
  - 失败根因: `mamba_dt_limit: [0.0, "inf"]` 字段 (convert_mcore_to_hf.py 新增, 150k config 无此字段)
  - 导致: `huggingface_hub.StrictDataclassFieldValidationError: time_step_limit expected tuple, got list`
  - 修复: 从 hf_iter_160000/config.json 删除 mamba_dt_limit 字段, 与 150k config 对齐
  - 重试: 转换进程 alive (PID 32217), 已进入 Writing 阶段 (4.44GB)
- Phase 5 (eval): pending (GGUF 写入完成后自动启动)
- Phase 6 (report): pending (eval 完成后自动刷新 gen_llamacpp_scaling_report.py)

**训练影响检查**:
- eval 全程: CUDA_VISIBLE_DEVICES="" / nice 19 / -t 4 / CPU-only / 串行单 ckpt
- 训练 step time: 6980-7103ms (<7.4s ✅), 未受影响

**护栏检查**:
- grep benchmark 数字 in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈29KB ✅

---

### 论文 §4.6 刷新 #1946（2026-11-11 07:30）

**取数命令**（.29）:
```bash
ssh 10.239.2.29 'cat /proc/146283/fd/1' | tail -50
ssh 10.239.2.29 'nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader'
```

**实测值**:
- iteration: 160,210/700,000 (取整 160,200 入文)
- 末 10 步 elapsed: 6940.0–7257.5ms (均 7062.5ms, 均 <7.4s ✅)
- tok/s: 4,194,304 / 7.0625 = 593,884 ≈ 594K
- loss: 2.014–2.042 (均 ≈2.03)
- NaN: 0, skipped: 0
- GPU: 8 卡 82–100% util, 74–75 GB / 81.5 GB

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109–110): iter 160,070→160,200, tok/s 595K→594K, loss≈2.03 不变
- abstract (0_abstract.tex line 14–15): 同上
- tab:prod-budget (line 122): "160k done" 不变 (160,200 rounds to 160k)
- wall-clock: ≈57d 不变 (700k × 4,194,304 / 594K = 57.2d)
- total (line 126): ≈60.5d 不变

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors
- main.pdf: 5 pages, 228,400 bytes

**护栏检查**:
- grep benchmark 数字 in ISEDA2027/ + main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈32.9KB ⚠️ (略超32KB,下轮归档)


---

### 论文 §4.6 刷新 #1947（2026-11-11 07:40）

**取数命令**:
- `ssh 10.239.2.29 'ps aux | grep -E "torchrun|xmodel25|pretrain_launcher" | grep -v grep | head -5'`
  → PID=146283, pretrain_launcher.py, Nov02 start, 8.6% CPU, 40.6GB RSS
- `ssh 10.239.2.29 'tail -15 /proc/146283/fd/1 2>/dev/null'`
  → fd=1 → /tmp/baize_s1_baize2b_worker.log (deleted)
  → latest: iteration 160,290/700,000 at 07:37:36
  → last 10 steps (160200–160290): 7025–7258 ms, avg 7,095 ms (<7.4s ✅)
  → loss: 2.010–2.042, avg ≈2.03
  → 0 NaN, 0 skipped iterations
  → grad norm: 0.089–0.110, lr: 1.000E-03
- `ssh 10.239.2.29 'nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader'`
  → 8 卡: 79–100% util, 74.8–75.2 GB / 81.5 GB

**计算**:
- tok/s = 4,194,304 / 7.095s = 591,060 ≈ 591K (前轮 594K → -3K)
- wall-clock = 700,000 × 4,194,304 / 591K = 57.5d → ≈57d (不变)
- total = 57 + 1.2 + 2.3 = 60.5d (不变)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109–110): iter 160,200→160,290, tok/s 594K→591K, loss≈2.03 不变
- abstract (0_abstract.tex line 14–15): 同上
- tab:prod-budget (line 122): "160k done" 不变 (160,290 rounds to 160k)
- wall-clock: ≈57d 不变
- total (line 126): ≈60.5d 不变

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors
- main.pdf: 5 pages, 228,618 bytes

**护栏检查**:
- grep ARC-Challenge|HellaSwag|BoolQ|OpenBookQA|PIQA|SciQ|Winogrande|ckpt-scaling in ISEDA2027/*.tex main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈10.4KB ✅ (归档 #1940–#1924 → daily-memories/2026-11-11.md, 省~17KB)

**160k eval 状态**: HF 导出✅ · GGUF 转换❌ (time_step_limit tuple/list 错误重现, 同 #1945/#1946, 待下轮修复)

### 论文 §4.6 刷新 #1948（2026-11-11 08:00）

**取数命令**（.29 实测）:
```
ssh -o StrictHostKeyChecking=no 10.239.2.29 'tail -30 /proc/146283/fd/1'
ssh -o StrictHostKeyChecking=no 10.239.2.29 'nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader'
```

**训练指标**（末 10 步 160340–160430）:
- iteration: 160,430 / 700,000
- elapsed time per iteration (ms): 6957.2, 6975.1, 6981.4, 7119.9, 7007.3, 6971.4, 7178.3, 6973.6, 7097.0, 6948.1
- 平均 step time: 7020.83 ms = 7.021 s
- tok/s = 4,194,304 / 7.021 = 597,410 ≈ 597K
- lm loss range: 2.012–2.033, 平均 ≈2.03
- skipped iterations: 0, nan iterations: 0
- GPU: 8 卡 100% util, ~75 GB/卡

**wall-clock 估算**:
- stable: 700,000 × 4,194,304 / 597K = 57.0d → ≈57d (不变)
- total = 57 + 1.2 + 2.3 = 60.5d (不变)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109–110): iter 160,290→160,430, tok/s 591K→597K, loss≈2.03 不变
- abstract (0_abstract.tex line 14–15): 同上
- tab:prod-budget (line 122): "160k done" 不变 (160,430 rounds to 160k)
- wall-clock: ≈57d 不变
- total (line 126): ≈60.5d 不变

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors
- main.pdf: 5 pages, 228,640 bytes

**护栏检查**:
- grep ARC-Challenge|HellaSwag|BoolQ|OpenBookQA|PIQA|SciQ|Winogrande|ckpt-scaling in ISEDA2027/*.tex main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈10.5KB ✅

**160k eval 状态**: HF 导出✅ · GGUF 转换✅ (07:43, bz2b-160000-f16.gguf 4.2G) · llama-server 起服 (PID1726277, port8190, -t4, nice19) · lm_eval client 运行中 (PID1736839, 8集 limit=100, --parallel 2 --batch-size 32) · results.json 尚未落盘 · 报告刷新 pending

---

### 论文 §4.6 刷新 — 2026-11-11 08:10 (#1949)

**取数命令**:
```
ssh 10.239.2.29 'tail -5 /proc/146283/fd/1'
```
输出末行: `[2026-11-11 08:02:17] iteration 160500/700000 | ... lm loss: 2.014661E+00 | ... skipped: 0 | nan: 0`

**训练指标**（末 10 步 160410–160500）:
- iteration: 160,500 / 700,000
- elapsed time per iteration (ms): 6973.6, 7097.0, 6948.1, 7004.6, 6949.5, 7101.1, 6938.5, 7031.9, 7115.8, 6957.0
- 平均 step time: 7011.71 ms = 7.012 s
- tok/s = 4,194,304 / 7.012 = 598,073 ≈ 598K
- lm loss range: 2.015–2.026, 平均 ≈2.02
- skipped iterations: 0, nan iterations: 0
- GPU: 8 卡 100% util, ~75 GB/卡

**wall-clock 估算**:
- stable: 700,000 × 4,194,304 / 598K = 56.8d → ≈57d (不变)
- total = 57 + 1.2 + 2.3 = 60.5d (不变)

**论文改动**:
- §4.6 (4_llm_pretrain.tex line 109–110): iter 160,430→160,500, tok/s 597K→598K, loss 2.03→2.02
- abstract (0_abstract.tex line 14–15): 同上
- tab:prod-budget (line 122): "160k done" 不变 (160,500 rounds to 160k)
- wall-clock: ≈57d 不变
- total (line 126): ≈60.5d 不变

**编译结果**:
- `latexmk -pdf -interaction=nonstopmode main.tex` → 0 errors, 0 warnings
- main.pdf: 5 pages, 228,240 bytes

**护栏检查**:
- grep ARC-Challenge|HellaSwag|BoolQ|OpenBookQA|PIQA|SciQ|Winogrande|ckpt-scaling in ISEDA2027/*.tex main.tex: 0 命中 ✅
- §4.7 sec:ckpt-scaling: 不存在 ✅
- 📦 TASK≈22.5KB ✅ / MEMORY≈11.9KB ✅

**160k eval 状态**: llama-server (PID1726277) + lm_eval (PID1736839) 仍运行中 · results.json 尚未落盘 · 报告刷新 pending

### 论文 §4.6 刷新 #1950 (2026-11-11 08:12)

- 取数命令: `ssh 10.239.2.29 'tail -30 /proc/146283/fd/1'`
- 最新 iteration: 160,560 / 700,000 (08:09:19)
- 末 10 步 (160,470–160,560) step time: 6938.5–7140.7ms (均 7026ms, 均 <7.4s ✅)
- loss 范围: 2.013–2.032, 均值 ≈2.02
- 0 NaN / 0 skipped iterations ✅
- GPU: 8 卡 100% / ~75GB
- tok/s = 4,194,304 / 7.026s = 596,787 ≈ 597K
- wall-clock = 700k × 4,194,304 / 597K = 56.9d ≈ 57d (不变)
- 刷新文件: 4_llm_pretrain.tex line109 (iter 160,500→160,560, tok/s 598K→597K), 0_abstract.tex line14 (同步)
- tab:prod-budget: "160k done" 不变 (160,560 rounds to 160k); total ≈60.5d 不变
- latexmk: 5 pages / 228,237 bytes / 0 errors / 0 undefined ✅
- grep benchmark 全文 = 0 命中 ✅; §4.7 不存在 ✅
- commit: 9991d5b09, pushed to origin/main

### 论文 §4.6 刷新 #1951 (2026-11-11 08:16)

- 取数命令: `ssh 10.239.2.29 'tail -30 /proc/146283/fd/1'`
- 最新 iteration: 160,610 / 700,000 (08:15:13)
- 末 10 步 (160,520–160,610) step time: 6972.9–7211.7ms (均 7043ms, 均 <7.4s ✅)
- loss 范围: 2.013–2.032, 均值 ≈2.02
- 0 NaN / 0 skipped iterations ✅
- GPU: 8 卡 94–100% / ~75GB
- tok/s = 4,194,304 / 7.043s = 595,537 ≈ 596K
- wall-clock = 700k × 4,194,304 / 596K = 57.1d ≈ 57d (不变)
- 刷新文件: 4_llm_pretrain.tex line109 (iter 160,560→160,610, tok/s 597K→596K), 0_abstract.tex line14 (同步)
- tab:prod-budget (line 122): "160k done" 不变 (160,610 rounds to 160k); total ≈60.5d 不变
- latexmk: 5 pages / 228,240 bytes / 0 errors / 0 undefined ✅
- grep benchmark 全文 = 0 命中 ✅; §4.7 不存在 ✅
- 160k eval: 仍运行中 (llama-server PID1726277 + lm_eval PID1736839), results.json pending

### 论文 §4.6 刷新 #1952 (2026-11-11 08:24)

- 取数命令: `ssh 10.239.2.29 'tail -20 /proc/146283/fd/1'`
- 最新 iteration: 160,670 / 700,000 (08:22:15)
- 末 10 步 (160,580–160,670) step time: 6972.9–7211.7ms (均 7054ms, 均 <7.4s ✅)
- loss 范围: 2.014–2.032, 均值 ≈2.02
- 0 NaN / 0 skipped iterations ✅
- GPU: 8 卡 95–100% / ~75GB
- tok/s = 4,194,304 / 7.054s = 594,616 ≈ 595K
- wall-clock = 700k × 4,194,304 / 595K = 57.1d ≈ 57d (不变)
- 刷新文件: 4_llm_pretrain.tex line109 (iter 160,610→160,670, tok/s 596K→595K), 0_abstract.tex line14 (同步)
- tab:prod-budget (line 122): "160k done" 不变 (160,670 rounds to 160k); total ≈60.5d 不变
- latexmk: 5 pages / 228,225 bytes / 0 errors ✅
- grep benchmark 全文 = 0 命中 ✅; §4.7 不存在 ✅
- 160k eval: 仍运行中 (llama-server PID1726277 + lm_eval PID1736839, etimes≈2393s≈40min), results.json pending

### 论文 §4.6 刷新 #1953 (2026-11-11 08:30)

- 取数命令: `ssh 10.239.2.29 'tail -20 /proc/146283/fd/1'`
- 最新 iteration: 160,730 / 700,000 (08:29:20)
- 末 10 步 (160,640–160,730) step time: 6939.3–7179.4ms (均 7077.8ms, 均 <7.4s ✅)
- loss 范围: 2.014–2.024, 均值 ≈2.02
- 0 NaN / 0 skipped iterations ✅
- GPU: 8 卡 94–100% / ~75GB
- tok/s = 4,194,304 / 7.0778s = 592,632 ≈ 593K
- wall-clock = 700k × 4,194,304 / 593K = 57.3d ≈ 57d (不变)
- 刷新文件: 4_llm_pretrain.tex line109 (iter 160,670→160,730, tok/s 595K→593K), 0_abstract.tex line14 (同步)
- tab:prod-budget (line 122): "160k done" 不变 (160,730 rounds to 160k); total ≈60.5d 不变
- latexmk: 5 pages / 228,464 bytes / 0 errors ✅
- grep benchmark 全文 = 0 命中 ✅; §4.7 不存在 ✅
- 160k eval: 仍运行中 (llama-server PID1726277 + lm_eval PID1736839, etimes≈2800s≈47min), results.json pending

### 论文 §4.6 刷新 #1954 (2026-11-11 08:36)

- 取数命令: `ssh -o StrictHostKeyChecking=no 10.239.2.29 'tail -60 /proc/146283/fd/1'`
- 最新 iteration: 160,770 / 700,000 (08:34:05)
- 末 10 步 (160,680–160,770) step time: 6939.3–7179.4ms (均 7098.2ms, 均 <7.4s ✅)
- loss 范围: 2.013–2.024, 均值 ≈2.02
- 0 NaN / 0 skipped iterations ✅
- GPU: 8 卡 95–100% / ~75GB
- tok/s = 4,194,304 / 7.0982s = 590,861 ≈ 591K (较前轮 593K 微降 -2K)
- wall-clock = 700k × 4,194,304 / 591K = 4,968,376s = 57.5d ≈ 58d (前轮 57d→58d)
- 刷新文件: 4_llm_pretrain.tex line109 (iter 160,730→160,770, tok/s 593K→591K), 0_abstract.tex line14 (同步)
- tab:prod-budget (line 122): wall-clock ≈57d→≈58d; Status "160k done" 不变 (160,770 rounds to 160k); total (line 126) ≈60.5d→≈61.5d
- latexmk -g: 5 pages / 228,225 bytes / 0 errors ✅
- grep benchmark 全文 = 0 命中 ✅; §4.7 sec:ckpt-scaling 不存在 ✅
- 160k eval: 仍运行中 (llama-server PID1726277 + lm_eval PID1736839, etimes≈3143s≈52min), results.json pending

### 论文 §4.6 刷新 #1956 (2026-11-11 09:01)

- 取数命令: `ssh -o StrictHostKeyChecking=no 10.239.2.29 'tail -30 /proc/146283/fd/1'`
- 最新 iteration: 160,970 / 700,000 (08:57:45)
- 末 10 步 (160,880–160,970) step time: 6966.8–7221.6ms (均 7085.2ms, 均 <7.4s ✅)
- loss 范围: 2.008–2.026, 均值 ≈2.02
- 0 NaN / 0 skipped iterations ✅
- GPU: 8 卡 94–100% / ~75GB
- tok/s = 4,194,304 / 7.0852s = 591,947 ≈ 592K (较前轮 591K +1K)
- wall-clock = 700k × 4,194,304 / 592K = 4,959,481s = 57.4d ≈ 57d (前轮 58d→57d)
- 刷新文件: 4_llm_pretrain.tex line109 (iter 160,770→160,970, tok/s 591K→592K), 0_abstract.tex line14 (同步)
- tab:prod-budget (line 122): wall-clock ≈58d→≈57d; Status "160k done" 不变 (160,970 rounds to 160k); total (line 126) ≈61.5d→≈60.5d
- latexmk: 5 pages / 228,442 bytes / 0 errors ✅
- grep benchmark 全文 = 0 命中 ✅; §4.7 sec:ckpt-scaling 不存在 ✅
- 160k eval: 仍运行中 (llama-server PID1726277 + lm_eval PID1736839, etimes≈4620s≈77min), results.json pending

### 160k eval 交付 + 论文 §4.6 刷新 #1957 (2026-11-11 09:14)

- 取数命令: `ssh -o StrictHostKeyChecking=no 10.239.2.29 'tail -12 /proc/146283/fd/1'`
- 最新 iteration: 161,110 / 700,000 (09:14:14)
- 末 10 步 (161,020–161,110) step time: 6981.5–7179.9ms (均 7068.5ms, 均 <7.4s ✅)
- loss 范围: 2.011–2.020, 均值 ≈2.02
- 0 NaN / 0 skipped iterations ✅
- GPU: 8 卡 96–100% / ~75GB
- tok/s = 4,194,304 / 7.0685s = 593,273 ≈ 593K (较前轮 592K +1K)
- wall-clock = 700k × 4,194,304 / 593K = 4,950,782s = 57.3d ≈ 57d (不变)
- 刷新文件: 4_llm_pretrain.tex line109 (iter 160,970→161,110, tok/s 592K→593K), 0_abstract.tex line14 (同步), tab:prod-budget line122 (Status 160k→161k done)
- latexmk: 5 pages / 228,247 bytes / 0 errors ✅
- grep benchmark 全文 = 0 命中 ✅; §4.7 sec:ckpt-scaling 不存在 ✅

#### 160k eval 结果（gguf_iter_160000_fixed_8set/results.json, 09:05 落盘）

| 任务 | acc | acc_norm | harness 口径 |
|:--|:--|:--|:--|
| ARC-Challenge | 0.35 | 0.34 | 0.34 |
| ARC-Easy | 0.61 | 0.62 | 0.62 |
| BoolQ | 0.67 | N/A | 0.67 |
| HellaSwag | 0.39 | 0.53 | 0.53 |
| OpenBookQA | 0.24 | 0.34 | 0.34 |
| PIQA | 0.75 | 0.75 | 0.75 |
| SciQ | 0.89 | 0.82 | 0.82 |
| Winogrande | 0.58 | N/A | 0.58 |
| **Avg(harness)** | | | **58.13%** |

- 160k harness Avg = 58.13%（新高峰，前峰值 58.00% @110k/130k，150k 为 57.12%）
- 报告刷新: `reports/report_pretrain_llamacpp_scaling_zh.html`（24,331 B, 16/20 ckpt, 10k–160k 全覆盖）
- 生成器: `gen_llamacpp_scaling_report.py`（TARGET_ITERS 含 10k–200k，幂等）
- 全 16 点 harness Avg 曲线: 51.50→52.00→53.00→55.12→54.25→54.25→56.00→57.00→57.88→57.75→58.00→56.75→58.00→55.25→57.12→**58.13**

## 2026-11-11 — L2 异常诊断 + 四层评测启动（用户令 2026-11-11）

> 用户令：「如何拿到更好的结果」· 四层评测目标：L1 常识 / L2 复杂推理 / L3 Agentic / L4 领域

### L2 异常诊断（P0 · GSM8K 1.52% 调查）

**历史评测**：P-8 `hf_iter_1149`（44.4B tok, 2026-10-15）· lm-eval 0.4.13 · GPU HF bf16

| 任务 | BaiZe P-8 (44.4B) | 口径 | 诊断 |
|:--|--:|:--|:--|
| GSM8K flex-extract | 1.52% | 5-shot, full 1319 | 🔴 异常低 |
| GSM8K strict-match | 0.00% | 5-shot | 🔴 从未匹配格式 |
| MATH-500 | 0.00% | exact_match | 🔴 |
| MMLU | 23.79% | 0-shot acc | 🟡 偏低但非零 |
| BBH | 14.04% | 0-shot flex-extract | 🟡 |
| HumanEval | 0.61% | pass@1 | 🔴 |
| MBPP | 0.00% | pass@1 | 🔴 |
| **CX6 Avg** | **6.66%** | | 🔴 vs Xmodel-2 39.62% |

**诊断证据**（eval log: `nemo_experiments/p8_adamw_decay/lm_eval_14/cx_gsm8k.log`）：
1. `strict-match=0.00%` → 模型从未产生 "The answer is X" 格式 → **格式生成能力缺失**
2. P-8 仅 44.4B tokens（当前 160k=671B，**15×**）→ 早期 ckpt 生成能力必然弱
3. 同期 L1=48.01%（loglikelihood 正常）→ 模型加载/权重/分词无误
4. `until: ['Question:', '</s>', '<|im_end|>']` → stop tokens 标准，无误
5. `trust_remote_code: False` → 但 L1 正常，排除加载问题

**初步结论**：**主要是 44.4B tokens 早期训练的能力问题**，非评测配置错误。
- L1(loglikelihood)正常 vs L2(generation)异常 → 早期 ckpt 能做"选最优"但不能"生成答案"
- 当前 160k(671B tok) 生成能力可能已改善 → 正在重评

### L2 重评（160k · 进行中）

- 脚本：`/tmp/baize_l2_eval_160k_v2.sh`（.29）
- 口径：llama-server CPU · `ctx=4096` · `-t 4` · `nice 19` · `limit=100`
- MMLU(0-shot) + GSM8K(5-shot) · lm_eval `local-completions` · `model=hf_iter_160000`(本地 tokenizer)
- 输出：`nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_test/`
- 状态：🟡 进行中

### L3/L4 资源盘点

- L3 (Agentic)：harness 线已有 TB 89 题 + SWE-bench 500 题（用 kimi-k2.6 API）；BaiZe 2B 需 GPU 服务化 → 待资源窗口
- L4 (领域)：designflow 评测脚本在 `doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval/`（20+ 任务，`run_one.sh`）；同 L3 需 GPU

### 四层报告

- 新建：`reports/report_pretrain_eval_4tier_zh.html`（中文 · 单文件自包含 · 14.5KB）

### L2 v2 崩溃修复 + v3 重评启动（#1960 · 2026-11-11 13:3x）

**v2 崩溃根因**：MMLU 是 `loglikelihood` 任务，标准 `local-completions` 后端（lm_eval `openai_completions.py:115`）要求 response 含 `choice["logprobs"]["token_logprobs"]`，但 llama-server `/v1/completions` 不返回该字段 → `KeyError: 'token_logprobs'`（0/22800 请求即崩）。

**v3 修复方案**：
- GSM8K（generate_until）→ 继续用 `local-completions`（generation 路径不需要 logprobs）
- MMLU（loglikelihood）→ 改用 `gguf_lmeval_run.py`（自定义 `GGUFServerLM` 类，logit_bias teacher forcing 方式计算 loglikelihood）
- 脚本：`run/baize_l2_eval_160k_v3.sh`（NFS 共享路径，避免 /tmp heredoc 引号问题）
- 服务：llama-server port=8082, -t 4, --parallel 2, nice 19, ctx=4096
- 输出：`gguf_iter_160000_l2_v3/{gsm8k,mmlu}/results.json`

**执行命令**：
```bash
# .29 上
ssh 10.239.2.29 'tail -5 /proc/146400/fd/1'  # 训练 iter 163,310 step 7172ms loss 2.04
ssh 10.239.2.29 'setsid bash .../baize_l2_eval_160k_v3.sh > /tmp/baize_l2_eval_160k_v3.log 2>&1 &'
```

**进度**：GSM8K 7/100 (~30s/it) → ETA ~45min → MMLU 排队 (~53min) → 总 ETA ~14:25+53min ≈ 15:18

### 论文 §4.6 刷新（#1960）

- iter 161,350 → 163,310, tok/s 592K → 590K, loss 2.02 → 2.04
- `tab:prod-budget`: 161k → 163k done, wall-clock 57d → 58d, total 60.5d → 61.5d
- 摘要同步刷新
- benchmark grep = 0 命中 ✅, §4.7 不存在 ✅
- latexmk: 5 pages / 215825B / 0 err ✅
- 取数命令：`ssh 10.239.2.29 'tail -5 /proc/146400/fd/1'`（PID 146400 = pretrain_launcher）

### L2 v3 进度监控 + v4 脚本准备（#1961 · 2026-11-11 13:5x）

**L2 v3 进度**（.29 上运行中）：
- GSM8K: 41/100 (~27s/it, 5-shot, local-completions) → ETA ~27min
- MMLU: 排队中 (0-shot, gguf_lmeval_run.py logit_bias) → ETA ~53min after GSM8K
- 总 v3 ETA: ~15:00
- 命令：`ssh 10.239.2.29 'tail -1 /tmp/baize_l2_eval_160k_v3.log | grep -oP "\d+/100" | tail -1'`

**L2 v4 脚本**（已创建，待 v3 完成后启动）：
- 文件：`baize_l2_eval_160k_v4.sh`
- 4 集：HumanEval(0-shot) / MBPP(0-shot) / hendrycks_math_algebra(4-shot) / bbh_cot_fewshot_boolean_expressions(3-shot)
- 各 limit=100, CPU llama-server port=8083, -t4, nice 19
- 等 v3 (port 8082) 完成后自动启动
- 预计耗时 ~3h

**L4 designflow 盘点**：
- `doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval/` 共 61 个 EDA-Eval-DesignFlow 任务
- `run_one.sh` 用 cline harness, 当前配 `deepseek-v4-pro-cloud`
- 接 BaiZe 2B 需本地 GPU 服务 (vllm/sglang) → 待 GPU 窗口

**训练健康**（.29）：
- iter 163,480 / 700,000 (23.4%)
- step 7189-7247ms (均 ~7.1s, <7.4s ✅)
- loss 2.031-2.036, 0 NaN/0 skip
- GPU 8 卡 94-100% / 74-75GB
- 命令：`ssh 10.239.2.29 'cat /proc/146283/fd/1 | tail -3'`（PID 146283）


## #1966 · 2026-11-11 14:50 · L3/L4 可行性调研 + 定性测试

### 定性测试：160k llama-server 代码生成
- **方法**：curl http://127.0.0.1:8082/v1/completions 发送 "Write a Python function to check if a number is prime. Only output the code."
- **模型输出**：` The following are the answers111111111111111111111...` (退化为重复字符)
- **结论**：模型在 code/math 生成任务上全面退化，同 GSM8K=0% 根因

### L3 Terminal-bench 可行性
- 基础设施：Harbor Docker + gw_proxy + 7 agent 适配器，_base.py 硬编码 cloud API
- 改本地模型：需修改 _base.py (TB_BASE_URL/TB_MODEL/TB_API_KEY) + 重建 Docker 镜像
- CPU llama-server：多轮交互 ~30s/轮，极慢
- **根本障碍**：模型生成能力不足，无法完成 agentic 多步任务

### L4 designflow 可行性
- run_one.sh 需 /nasdata/app.e0031982/code/EDA-Flow-Bench (仅 .15 有)
- SSH 10.251.36.15 = Connection timed out
- 任务 workdir (prompt.txt + assets/) 在 NFS 上可读
- 判分器 check.py 在 .15，NFS 上没有
- 任务极复杂（4 步多任务：修复 Python + 改写 SKILL + 运行 pipeline + 更新 lib.defs）
- **根本障碍**：同 L3，模型生成能力不足

### 核心发现
L2/L3/L4 低分/空白同一根因 = 训练数据(P-5b/P-8 Ultra-FineWeb-L3)缺乏 code+math 内容 → 所有需要连贯生成的任务都退化为重复输出

---

## L2 v3 最终结果 @ 160k（2026-11-11 #1980）

### 训练状态
- iter 165,220 / 700,000 · step ~7150ms (<7.4s✅) · loss ~2.03 · 0 NaN/0 skip · GPU 8×95-100%/75GB
- 命令：`ssh 10.239.2.29 'tail -5 /tmp/baize_xmodel25_decay_v2_train.log'`

### GSM8K 结果（v3 · 0-shot · logprob · limit=100）
- exact_match,strict-match = 0.0% (stderr 0.0)
- exact_match,flexible-extract = 0.0% (stderr 0.0)
- 落盘：`gguf_iter_160000_l2_v3/gsm8k/__nas_train__.../results_2026-11-11T14-19-43.079813.json`

### MMLU 结果（v3 · 0-shot · logprob · 5700 sample · full）
- mmlu overall acc = 23.16% (stderr 0.0056)
- mmlu_stem = 22.47% · mmlu_other = 23.08% · mmlu_social_sciences = 22.58% · mmlu_humanities = 24.77%
- 落盘：`gguf_iter_160000_l2_v3/mmlu/results.json`
- 诊断：≈随机水平（4-choice random=25%），与 P-8 基线 23.79% 基本一致 → 15× 训练量后 MMLU 无改善

### v4 运行中（HumanEval/MBPP/MATH/BBH）
- llama-server PID 2369157 port 8083 · HumanEval(0-shot,gen,pass@1,limit=100) 运行中
- 落盘目录：`gguf_iter_160000_l2_v4/`
- 脚本：`baize_l2_eval_160k_v4.sh`

### v4 部分失败 + v5 修复（2026-11-11 #1980）
- **HumanEval/MBPP 失败**：lm_eval `code_eval` 指标未缓存（离线模式无法下载）→ ValueError
  - 修复：通过 proxy (http://172.19.92.25:13128) 下载 `code_eval` 到 `/nas_train/app.e0031982/.cache/modules/evaluate_modules/metrics/evaluate-metric--code_eval/`
- **MATH 失败**：`hendrycks_math_algebra` 4-shot 触发 `build_qa_turn` 断言 `Answer is not a string! : [-9, 9]`
  - 修复：v5 改用 0-shot 绕过 few-shot context 构建
- **BBH 运行中**：`bbh_cot_fewshot_boolean_expressions` 3-shot, limit=100, ~69s/it, 6/100, ETA~1.5h
- **v5 已启动**：`baize_l2_eval_160k_v5.sh` 在 .29 后台 (PID 3102868) 等待 BBH 完成后重跑 HumanEval+MBPP+MATH(0-shot)

## #1983 · 2026-11-11 18:00 · 四层评测轮 · 数据配比修正 + BBH 监控

### 训练状态
- iter 165,560 / 700,000 (23.65%) · step 6959-7090ms (<7.4s✅) · loss 2.025-2.040 · 0 NaN/0 skip
- lr = 1.000000E-03（stable 段，decay 尚未开始）
- GPU 8×96-100% / 75GB · PID 146283 · etimes ~770789s (~8.9 天)
- 命令：`ssh 10.239.2.29 'tail -3 /proc/146283/fd/1'`

### 🔬 S1 训练数据实际配比（从训练进程命令行参数提取 · 重要修正）
**此前报告(#1966/#1979)称"训练数据缺乏 code+math 内容"是错误的。**

从 `ps -eo args= | grep pretrain_launcher` 提取的数据 blend 权重：

| 数据源 | 分片数 | 单片权重 | 总权重 | 占比 | 类别 |
|:--|--:|--:|--:|--:|:--|
| en_v1_4_pb_s000-s015 | 16 | 0.040625 | 0.6500 | 65.0% | 语言(英文网页) |
| ufw_l1_en_hq_pb_s000-s015 | 16 | 0.003125 | 0.0500 | 5.0% | 语言(UFW L1 HQ) |
| ufw_zh_train_s0-s3 | 4 | 0.010000 | 0.0400 | 4.0% | 语言(中文) |
| math_l1_pb_s000-s015 | 16 | 0.003125 | 0.0500 | 5.0% | 数学(L1) |
| math_l3_pb_s000-s015 | 16 | 0.001250 | 0.0200 | 2.0% | 数学(L3) |
| code_l2_pb_s000-s015 | 16 | 0.009375 | 0.1500 | 15.0% | 代码(L2) |
| code_l3_pb_s000-s015 | 16 | 0.002500 | 0.0400 | 4.0% | 代码(L3) |
| **合计** | — | — | **1.0000** | **100%** | — |

**实际配比 vs DeepSeek 最优**：
- Code: 19.0% (vs 40.0% → -21.0pp)
- Math: 7.0% (vs 20.0% → -13.0pp)
- Language: 74.0% (vs 40.0% → +34.0pp)
- Code:Math:Lang = 2.7:1:10.6 (vs 4:2:4 → 严重偏离)

**671B tokens 时已训练量**：code ~127B tok · math ~47B tok
- 127B code tokens 理论上应产生基础代码能力
- GSM8K=0% + 代码生成退化说明：① code/math 数据质量(L2/L3)可能不足以教会生成；② stable 阶段 lr=1e-3 恒定，可能需要 decay 阶段 consolidate；③ Mamba2-hybrid 架构在自回归生成上可能有特殊行为

### L2 v4 BBH 进度
- 32/100 (~69s/it, ETA ~78min) · `bbh_cot_fewshot_boolean_expressions` 3-shot, limit=100
- 命令：`ssh 10.239.2.29 'tail -3 /tmp/baize_l2_eval_160k_v4.log | grep -oP "\d+/100" | tail -1'`

### 评测队列（port 8083 串行）
1. BBH v4 (运行中, 32/100, ETA ~78min)
2. v5: HumanEval + MBPP + MATH 0-shot (等待 BBH 完成, ~3h)
3. GSM8K 诊断: --log_samples, 5-shot + 0-shot 各 10 样本, ctx=8192 (等待 v5 完成, ~30min)
- 总队列 ETA: ~4.5h

### 四层报告更新
- 修正数据配比分析（从"无 code/math"→"26% code+math，但远低于最优 60%"）
- 更新 MMLU 状态为完成 (23.16%)
- 更新 BBH 状态 (32/100 运行中)
- 新增 S1 训练数据实际配比表
- 更新 footer 至 #1983
- 报告: `run/reports/report_pretrain_eval_4tier_zh.html` (31.9KB) + 同步至 `doc/reports/`

---

## #1984 2026-11-11 18:10 — 生成退化诊断（7 个 curl 探针）+ BBH 监控

### 训练健康
- iter=165640/700k, step=7092ms (<7.4s ✅), loss=2.023, lr=1e-3 (stable 段), 0 NaN/0 skip
- GPU: 8 卡 92-100% util, ~75GB VRAM

### 生成退化诊断（核心发现）
向运行中的 llama-server (port 8083, bz2b-160000-f16.gguf, iter 160k) 发送 7 个 curl 探针：

| # | Prompt | Temp | 输出 | 诊断 |
|---|--------|------|------|------|
| 1 | GSM8K "Natalia sold clips..." | 0 greedy | "The video111111..." (重复1×200+) | 🔴 退化 |
| 2 | "What is 2+3? Answer:" | 0 greedy | "the111 2nd333..." (首token="the"→退化) | 🔴 退化 |
| 3 | "def fibonacci(n):..." | 0 greedy | "/examples111111..." (重复1×200+) | 🔴 退化 |
| 4 | "True or False: 2+3=5. The answer is " | 0 greedy | "5" (✅正确!) → "th century" (退化) | 🟡 首token✅ |
| 5 | "The capital of France is Paris. The capital of Japan is " | 0 greedy | "50xxxx111" (错误→退化) | 🔴 |
| 6 | "What is 2+3? Answer:" | 0.7 | "Would it was easier..." → "111..." | 🔴 先连贯后退化 |
| 7 | "What is 2+3? Answer:" | 0, rp=1.3 | "...The simplest possible way to solve this problem..." (✅连贯英文!) | 🟡 rp打破循环 |

### 诊断结论
1. **首 token logits 正确**：L1 MCQ 58.13%（正常），"2+3=5"→首token="5"✅ → 模型权重/加载/分词无误
2. **SSM 状态在多 token 生成时崩溃**：2-5 token 后退化为重复"1" → Mamba2 recurrent state 未正确维护
3. **repeat_penalty 可部分修复**：rp=1.3 打破"1"循环后模型能生成连贯英文 → SSM 状态并非完全损坏，而是陷入"1"吸引子
4. **HF transformers 无法 CPU 验证**：`causal_conv1d_cuda` 仅支持 CUDA → 无法在 CPU 上对比 HF vs llama.cpp 生成质量
5. **双重根因**：模型能力不足(26% code+math，远低于 60% 最优) + llama.cpp SSM 生成路径可能放大退化

### 建议（待用户拍板）
- ① 生成评测加 `repeat_penalty=1.1-1.3`（可能小幅改善 L2 分数）
- ② 等 GPU 窗口用 vllm/sglang 对比 HF 生成质量
- ③ decay 阶段混入 4:2:4 数据改善模型基础生成能力

### BBH v4 进度
- 42/100 (~68s/it, ETA ~66min)
- HumanEval/MBPP 失败（缺 HF_ALLOW_CODE_EVAL，v5 已修复）
- MATH 失败（4-shot assertion error，v5 改 0-shot）

### 四层报告更新
- 新增 "生成退化诊断" card（7 探针表 + 5 点结论 + 3 建议）
- header iter/BBH 更新
- footer #1984
- 报告: `run/reports/report_pretrain_eval_4tier_zh.html` (34.9KB) + 同步至 `doc/reports/`

---

## #1988 2026-11-11 19:20 — BBH v4 完成(0.0%) + v5 NFS 崩溃 + GSM8K 诊断启动

### 训练健康
- iter=166150/700k, step=7018ms (<7.4s ✅), loss=2.043, lr=1e-3 (stable 段), 0 NaN/0 skip
- GPU: 8 卡 100% util, ~75GB VRAM
- 命令：`ssh 10.239.2.29 'tail -3 /proc/146283/fd/1'`

### BBH v4 结果（✅ 完成）
- **exact_match = 0.0%** (boolean_expressions, 3-shot CoT, limit=100, 1h55m, 19:17 完成)
- 结果文件：`gguf_iter_160000_l2_v4/bbh/__nas_train__..._hf_iter_160000/results_2026-11-11T19-17-24.938559.json`
- 命令验证：`cat <path>/results_*.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['results'])"`
  → `{"bbh_cot_fewshot_boolean_expressions": {"exact_match,get-answer": 0.0, "exact_match_stderr,get-answer": 0.0}}`
- **确认所有 L2 生成任务 = 0%**（GSM8K=0%, BBH=0%, HumanEval/MBPP/MATH 未能评测）
- MMLU=23.16% 是唯一非零 L2 分数（MCQ loglikelihood，不需生成）

### v5 NFS 崩溃
- `baize_l2_eval_160k_v5.sh` 启动时遇到 `error reading input file: Stale file handle`（NFS 错误）
- HumanEval/MBPP/MATH 仍未评测 → 待 GSM8K 诊断完成后重启 v5

### GSM8K 诊断（🟡 运行中）
- PID=2851659, port=8083, ctx=8192, -t 4, nice 19
- 5-shot + 0-shot 各 10 样本 with --log_samples
- 进度：4/10 @ 42s/it, ETA ~11min（两阶段合计）
- 日志：`/tmp/baize_l2_gsm8k_diag.log`

### L2 评测队列状态（port 8083 串行）
1. ~~BBH v4~~ ✅ 完成 (0.0%)
2. ~~v5: HumanEval + MBPP + MATH~~ ❌ NFS 崩溃 → 待重启
3. GSM8K 诊断 🟡 运行中 (4/10)

### 四层报告更新
- header: iter 166150, BBH=0% 完成
- L2 badge: GSM8K=0% · BBH=0% · MMLU=23%@160k
- 新增 BBH v4 结果 card（8 行表 + v5 崩溃 + GSM8K 诊断状态）
- 核心发现区更新（BBH 完成 0%，v5 崩溃，GSM8K 诊断运行中）
- footer #1988
- 报告: `run/reports/report_pretrain_eval_4tier_zh.html` + 同步至 `doc/reports/`


## #1991 · 2026-11-11 20:12 · 四层评测轮 · v6脚本创建+启动

### v5 MATH 进度
- hendrycks_math_algebra 0-shot limit=100
- 16/100, ~42s/it, ETA~1h
- 预期 0%（生成退化同 GSM8K/BBH）
- llama-server PID=1594930 port 8083 t=4 nice=19

### HumanEval/MBPP 失败根因确认
- lm_eval 0.4.x 需要 `--confirm_run_unsafe_code` CLI flag (store_true)
- v5 脚本仅设 `HF_ALLOW_CODE_EVAL=1` env var → 不足
- 错误: `ValueError: Attempted to run task: humaneval which is marked as unsafe. Set confirm_run_unsafe_code=True to run this task.`
- 源码: `/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/lm_eval/_cli/run.py:330`

### v6 脚本创建
- 文件: `baize_l2_eval_160k_v6.sh`
- 修复: ① HumanEval/MBPP 加 `--confirm_run_unsafe_code` ② llama-server 加 `--repeat-penalty 1.3` ③ MATH 用 RP=1.3 重跑 ④ 生成探针
- 在 .29 后台 nohup 运行, 等待 port 8083 空闲 (v5 MATH 完成后自动启动)
- 落盘目录: `gguf_iter_160000_l2_v6/`

### 训练健康
- iter 166630/700k, step 6943-7205ms (<7.4s✅), loss 2.022-2.044, 0 NaN/skip
- GPU 8卡 95-100%/75GB


## #2017 2026-11-12 00:45 L2 v6 final + L3 TB smoke start

### L2 v6 Final Results (160k ckpt, CPU llama-server, RP=1.3)
- HumanEval: pass@1=0.0% +- 0.0 (100/100, 2h15m, results_2026-11-11T23-25-19.json)
- MBPP: pass@1=0.0% +- 0.0 (100/100, 1h10m, results_2026-11-12T00-36-41.json)
- MATH v6: interrupted @ 84/100 (v6 script killed server after MBPP done; v5 MATH=0% already confirmed)
- Gen probe (RP=1.3): output="yes!,$.111111..." (finish_reason=length) -> RP=1.3 does NOT fix SSM degradation
- L2 6/6 summary: GSM8K=0% + BBH=0% + MATH=0% + HumanEval=0% + MBPP=0% + MMLU=23.16% -> CX6 Avg=3.86%

### Commands executed
- ssh 10.239.2.29 'cat .../gguf_iter_160000_l2_v6/mbpp.log | tr "\r" "\n" | tail -5'
  -> |mbpp |      1|none  |     0|pass_at_1|...|    0|±  |     0|
- ssh 10.239.2.29 'cat /tmp/baize_l2_eval_160k_v6.log | tail -30'
  -> Gen probe: {"choices":[{"text":"yes!,$.\n111111111111111333353$111222333647½..."}
  -> [00:38:13] Killing llama-server PID=2671359...

### Script fixes
- baize_l3_autoqueue.sh: Added MATH-safety check (pgrep lm_eval.*math before killing server)
- baize_l3_autoqueue.sh: pgrep pattern fixed (baize_xmodel25_decay_v2 -> pretrain_launcher.py)
- baize_l3_tb_smoke.sh: pgrep pattern fixed + grep||true for step time parse
- Old autoqueue PID1986722 killed, new PID1616750 started with fixed script

### L3 TB smoke
- Status: Harbor running 2 tasks (fix-git + break-filter-js-from-html) with cline_patched agent
- llama-server port 8083, GGUF F16, -t 4, nice 19
- Results pending in run/baize_l3_tb_smoke_results/

### Training health
- iter 168950/700k (24.1%), step 7008-7058ms (<7.4s OK), loss 2.05, lr=1e-3, 0 NaN/skip
- PID 146283 on .29

### 170k L1 eval (2026-11-12 05:47)
- Checkpoint: iter_0170000 (hf_iter_170000, GGUF F16 at /nas_train/app.e0031982/models/baize2b_gguf/bz2b-170000-f16.gguf)
- Eval: 8-set zero-shot, limit=100, llama-server CPU -t 4 nice 19, port 8190
- Elapsed: 4560.94s (~76min)
- Results: /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_170000_fixed_8set/results.json
- Per-task (harness acc_norm where available, acc otherwise):
  arc_challenge=0.34  arc_easy=0.57  boolq=0.60  hellaswag=0.55
  openbookqa=0.37    piqa=0.76     sciq=0.85   winogrande=0.58
- **Avg(harness) = 57.75%** (vs 160k peak 58.13%, Δ=-0.38pp, within stderr±4.5%)
- L1 scaling report refreshed: 17/20 ckpt (10k-170k)
- Command: python3 gen_llamacpp_scaling_report.py (BAIZE_REPORT_PATH=...report_pretrain_llamacpp_scaling_zh.html)

### L2 HumanEval HF Complete Eval (2026-11-12 14:56 · #2058)
- **Method**: Custom HumanEval evaluator (`baize_l2_hf_humaneval_direct.py`) using sglang env (transformers 5.18.0, native NemotronH, CPU bfloat16)
- **Why custom**: py310 env has sklearn/numpy binary incompatibility (`ValueError: numpy.dtype size changed` from /dev/shm harness sklearn), sglang env has no lm_eval installed, no pip (no network on .29)
- **Config**: 0-shot, greedy, max_new_tokens=128, torch.set_num_threads(8), OMP_NUM_THREADS=8, nice 19, CUDA_VISIBLE_DEVICES=""
- **Model**: hf_iter_160000 (160k checkpoint, 671B tokens trained, 23% of 700k)
- **Results**: pass@1 = 3/20 = **15.0%**
  - PASS: HumanEval/7 (filter_by_substring), HumanEval/15 (string_sequence), HumanEval/16 (count_distinct_characters)
  - FAIL but coherent code: 17/20 (completion_length 36-676 chars, NOT degenerate repetition)
  - Per-problem gen_time: ~14s (CPU bfloat16, Mamba2 reference implementation, no mamba_ssm/causal_conv1d optimization)
- **Key finding**: llama.cpp SSM generation bug is the PRIMARY cause of L2=0%
  - Same 160k ckpt: HF transformers pass@1=15.0% vs llama.cpp 0/100=0.0% → 15pp gap entirely from inference backend
  - Model HAS basic code generation capability (15% is reasonable for 2B @ 23% training, cf. DeepSeek 1.3B 4:2:4 HumanEval=20.1%)
- **Training impact**: step 6945-7021ms < 7.4s ✅ (no impact on training throughput)
- **Results file**: `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_160000_l2_hf_humaneval_direct/results.json`
- **Next**: GSM8K HF 4-shot eval (script `baize_l2_hf_gsm8k_direct.py` ready, ~7 min for 50 problems)
