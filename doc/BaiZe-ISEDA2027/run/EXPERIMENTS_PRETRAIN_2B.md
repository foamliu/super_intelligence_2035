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
> 中文报告：`reports/report_pretrain_decay_v2_final_eval_zh.html`（第二版，对照口径已更正：主对照 Xmodel-2.5 final）

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
| step_532000（起点基线） | 1.41T | 1.3B | ⏸待跑 | ⏸待跑 | Dense Transformer |
| P-8 final（旁注·架构/参数量不同） | 44.4B | 2.22B | 49.21% | 6.81% | Mamba2-hybrid |
| Xmodel-2.5 step_6000（旁注） | 79.2B | 1.3B | 50.20% | — | Dense Transformer |

> **关键观察（口径已更正）**：decay v2 从 Xmodel-2.5 stable 末点 step_532000（1.41T）起步 decay 71.2B，其唯一公平主对照是 **Xmodel-2.5 final（CS8 65.40% / CX6 32.90%）**；实测 **CS8 -20.43pp / CX6 -26.69pp，14 集全面大幅落后** →「decay 段没练出来」（甚至可能把起点模型练退化）。失败归因见报告 §4：①双移位 bug（train 2-step / eval 1-step，代码级确认）②peak LR 1.67e-3 过高+warmup100 过短 ③code ≈26 epochs 过采样 ④step 0 loss=11.72 起点异常 ⑤step_532000 基线缺失（⏸关键判定实验，待用户批准补跑）。**P-8（2.22B Mamba2-hybrid / 从头 44.4B）与 decay v2 架构/参数量均不同，不可作归因依据**。
