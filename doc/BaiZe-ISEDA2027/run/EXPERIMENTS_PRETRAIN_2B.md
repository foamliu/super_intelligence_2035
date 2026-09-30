# EXPERIMENTS_PRETRAIN_2B.md — BaiZe Stage(i) Mamba2-hybrid 2B 预训练超参搜索实验记录

> 骨架固定：Mamba2-hybrid（56 层 Nemotron-H 式顺序混合，**2.220B** 真实参数量）。
> 固定口径（跨配置一致）：8 卡（10.239.2.29，TP1/DP8）/ GBS=8 / mb=1 / seq=4094 / bf16 / AdamW(β1=0.9 β2=0.95 eps=1e-5 wd=0.1) / seed=1234 / eval 关闭（eval_iters=0）。
> 数据：`data/ultrafineweb_l3_qa`（200k docs / 164.75M token），总样本 40243（seq4094）。
> 短地平线 5000 步/组 ≈ 164M token；长跑 S5-01 20000 步（需补切 ≥700M token）。

## 胜出配置（未定，S0–S5 进行中）

## 实验记录表
| ID | 阶段 | stable LR | 调度族 | decay/warmup/min_lr | 退火混合 | 状态 | val loss | 训练tok/s | 耗时 | GPU·h | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| S0-01 | S0 | — | WSD | — | — | ✅ done | — | ~99K | ~2.2min | ~0.3 | 8 卡冒烟 30 步，稳态 ~330ms/iter，loss 7.90@30，WSD 调度验证通过 |
| S1-01 | S1 | 3e-4 | WSD | 500/250/3e-5 | — | 🟡 running | — | — | ~28min(ETA) | ~3.7(ETA) | baseline，5000 步，lr3e-4 |
| S2-01…S2-07 | S2 | 2e-4…1e-3 | WSD | 500/250/3e-5 | — | ⏳ | — | — | — | — | 待 S1 完成后逐点扫描 |
| S3-01…S3-05 | S3 | 胜出 LR | 变 | 变 | — | ⏳ | — | — | — | — | 待 S2 |
| S4-01…S4-03 | S4 | 胜出 | 胜出 | 胜出 | 变 | ⏳ | — | — | — | — | 待 S3 |
| S5-01…S5-04 | S5 | 胜出 | 胜出 | 胜出 | 胜出 | ⏳ | — | — | — | — | 待 S4 |

## S0 冒烟实测（2026-09-30）
- 8×H100，TP1/DP8，30 步从零（seq4094/GBS8/mb1/bf16，WSD warmup3/decay3 仅冒烟用）。
- 稳态 **~330ms/iter** ≈ **~99K tok/s**；首 10 步均 12.6s/iter（首步 SSM 编译 + CUDA-graph 一次性）。
- loss：11.37(iter10) → 8.43(iter20) → **7.90(iter30)**；grad norm 2.98→1.35，无 NaN/skip。
- WSD 调度确认：LR 3e-4(stable) → 3e-5(decay 尾，min_lr)。
- ckpt `nemo_experiments/s0_smoke_8gpu/checkpoints/iter_0000030`（torch_dist）。
- 总样本 40243（seq4094）；5000 步需 40000，余 243（0.6% margin，偏紧，S1 观察）。