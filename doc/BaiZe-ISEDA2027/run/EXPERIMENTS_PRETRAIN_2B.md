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
| S1-01 | S1 | 3e-4 | WSD | 500/250/3e-5 | — | ✅ done | 2.849@5000 | ~99K(独占) | ~41min | ~5.5 | baseline 5000 步，loss 7.90@30→2.849@5000；⚠️ 被同行 vision 抢占 GPU0~5，step time 330→850ms，tok/s 基线下沉 |
| S2-01…S2-07 | S2 | 2e-4…1e-3 | WSD | 500/250/3e-5 | — | 🟡 running | — | — | — | — | 7 点串行 sweep（`baize_s2_sweep.sh`），逐点 5000 步；明细见下方「S2 LR 扫描明细」，S2-01/S2-02 已完成、S2-03 running |
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

## S2 LR 扫描明细（WSD 固定，7 点 × 5000 步，8 卡 TP1/DP8）
| ID | stable LR | final loss@5000 | grad norm | skip/nan | 耗时 | GPU·h | 状态 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| S2-01 | 2e-4 | **2.9037** | 0.543 | 0/0 | ~28.8min | ~3.8 | ✅ done |
| S2-02 | 3e-4 | **2.8462** | 0.455 | 0/0 | ~27.1min | ~3.6 | ✅ done |
| S2-03 | 4e-4 | **2.8167** | 0.414 | 0/0 | ~26.8min | ~3.6 | ✅ done |
| S2-04 | 5e-4 | — | — | — | — | — | 🟡 running |
| S2-05 | 6e-4 | — | — | — | — | — | ⏳ |
| S2-06 | 8e-4 | — | — | — | — | — | ⏳ |
| S2-07 | 1e-3 | — | — | — | — | — | ⏳ |

## S5-01 数据补切（≥700M token ✅ 完成，2026-09-30 13:16）
- `preprocess_data.py --input-dir .../Ultra-FineWeb-L3/.../qa --output-prefix data/ultrafineweb_l3_qa_700m --max-docs 900000`。
- ✅ 完成：**900000 docs / 741,712,139 tokens（≈742M ≥ 700M 门限）**，产物 `data/ultrafineweb_l3_qa_700m.bin`(2.97GB)/`.idx`(18MB)/`.json`。S5-01（20000 步≈655M）数据就绪。