# BaiZe 2B 架构搜索记录（从零训练）

## 胜出架构（待 S4 填写）

## 对比结论（loss / 训练速度 / 推理速度 三张表，待填）

## S1 冒烟结果（arch_prepare，2026-09-29）
- 两架构均已「从零随机初始化」跑通 10 步前向+反向 + 保存 checkpoint（torch_dist）。
- 统一路径：NVIDIA/NeMo recipe（`pretrain(pretrain_config(...), forward_step)`，torchrun 直驱，nemo_run 未装已 bypass）。
- 统一 tokenizer：DeepSeek-V4.1-Flash（追加 EOD 后 vocab=129281，模型侧 pad 129408）。
- **⚠️ 两架构非等参**：MiniCPM5-2B ≈ **2.51B**（transformer 1.98B + embedding 0.53B）；Mamba2-hybrid ≈ **3.00B**（transformer 2.47B + embedding 0.53B）。差 ~19.5%，属「非等参对比」（>10%），报告需注明。
- **⚠️ Mamba2 冒烟初始 loss 偏低（8.80 vs MiniCPM 11.62）**：理论上随机初始化应 ≈ ln(129408)=11.77，Mamba 的 8.80 异常，需在正式训练确认（可能是 SSM 归纳偏置或 init 异常）。

### 冒烟明细（TP=2 / mock 数据 / 10 步）
| 架构 | 参数量(实测) | 初始 loss | 耗时/iter | 保存 ckpt |
|:---|:---|:---|:---|:---|
| MiniCPM5-2B (42层 Llama) | 2.51B | 11.62 | ~1462 ms | ✅ |
| Mamba2-hybrid (56层) | 3.00B | 8.80 ⚠️ | ~11619 ms | ✅ |

## S2 1000 步训练口径（决策 3，两架构完全一致，2026-09-29 晚启动）
- 两架构均 6 卡（A1→10.239.2.29 GPU0~5；A2→10.239.2.12 GPU0~5），TP=1 / DP=6
- seq_length=4096、micro_batch_size=1、**global_batch_size=6**（24.5K tok/步，无梯度累积）
- optimizer=distributed AdamW（β1=0.9 β2=0.95 eps=1e-5 wd=0.1）、lr=3e-4（cosine→min_lr=3e-5，warmup=100）
- train_iters=1000、random_seed=1234、bf16、eval 关闭（eval_iters=0）、数据=同一份 DeepSeek .bin/.idx（200k docs/164.75M tokens）
- **GBS=6 理由（关键）**：Mamba2 SSM ~11.6s/步，GBS>6 会让 Mamba2 训练远超 20 GPU·h 预算（GBS=128≈408 GPU·h）。故定 GBS=6（Mamba2 ≈3.2h×6卡≈19.3 GPU·h）。属「早期收敛」对比（约 24.6M tokens/架构）。

## 实验记录
| ID | 架构 | 参数量 | 状态 | 最终loss | 训练tok/s | 耗时 | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| A1-01 | MiniCPM5-2B(42层 Llama) | 2.51B | running | - | ~91K（270ms/iter） | - | 从零，2.29 GPU0~5 |
| A2-01 | Mamba2-hybrid(56层) | 3.00B | running | - | ~2.1K（~11.6s/iter 预估） | - | 从零，2.12 GPU0~5，非等参(+19.5%) |
