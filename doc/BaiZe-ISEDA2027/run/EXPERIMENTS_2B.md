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
| ID | 架构 | 参数量 | 状态 | 最终loss | 训练tok/s | 耗时/iter | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| A1-01 | MiniCPM5-2B(42层 Llama) | 2.51B | ✅ done | **4.8065**（11.62→4.81） | **~89K** | ~275ms | 从零，2.29 GPU0~5 |
| A2-01 | Mamba2-hybrid(56层) | 3.00B | ✅ done | **4.6846**（10.80→4.68） | **~72K** | ~340ms | 从零，2.12 GPU0~5，非等参(+19.5%) |

## S2 训练结果（1000 步，已完成 2026-09-29）
- **loss 曲线**：MiniCPM5 11.62→4.8065（Δ6.81）；Mamba2 10.80→4.6846（Δ6.12）。Mamba2 终值更低（-0.122），但多 ~19.5% 参数（非等参，需注明）。
- **训练吞吐**：MiniCPM5 ~275ms/iter（≈89K tok/s）；Mamba2 ~340ms/iter（≈72K tok/s）。**MiniCPM5 快 ~24%**。
  - ⚠️ Mamba2 首步 ~12.3s 是 SSM 编译/CUDA-graph 捕获的一次性开销，稳态 ~340ms。此前「11.6s/iter」为冒烟首步假象。
- **Mamba2「初始 loss 8.80」已澄清**：真值首步 loss=10.80（≈ln(129408)=11.77，正常），此前 8.80 是 mock 数据冒烟测得多步后的值，非异常。
- **checkpoint**：MiniCPM5 `nemo_experiments/minicpm5_2b_1000step/checkpoints/iter_0001000`（12 distcp，~4.9GB）；Mamba2 `nemo_experiments/mamba2_2b_1000step/checkpoints/iter_0001000`（~4.3GB）。
- Δloss-per-parameter 观感：Mamba2 容量更大收敛略快但吐字慢；等参下优劣需 S3 推理性价 + 报告权衡。

## S3 推理基准（下一步）
- 待办：① NeMo ckpt→HF 权重转换（MiniCPM5=Llama 体系较简单；Mamba2-hybrid 自定义结构需手写转换）；② SGLang 起服测生成 tok/s（本环境 vLLM import 崩 `undefined symbol _ZN3c104cuda9SetDeviceEa`，用 SGLang 替代，沿用 1B 任务路径）；③ 记录 prompt 处理 + 生成 tok/s 对比。
